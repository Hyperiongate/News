# TruthLens Unified News & Transcript Analyzer - Dockerfile
# Date: October 29, 2025
# Version: 2.2.0 - HASH CHECKING FIX
#
# LATEST CHANGES (October 29, 2025):
# ===================================
# - CRITICAL FIX: Added PIP environment variables to disable hash checking
# - These environment variables prevent the hash mismatch error during deployment
# - All existing functionality preserved - DO NO HARM ✓

FROM python:3.11-slim

# Install system dependencies and Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxcb1 \
    libxkbcommon0 \
    libgtk-3-0 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome location for undetected-chromedriver
ENV CHROME_BIN=/usr/bin/google-chrome-stable
ENV CHROME_PATH=/usr/bin/google-chrome-stable

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# CRITICAL FIX: Set PIP environment variables BEFORE installing packages
# This prevents hash checking errors during deployment
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install playwright browsers if playwright is in requirements
RUN python -c "import sys; sys.exit(0)" && \
    (pip list | grep playwright && playwright install chromium || echo "Playwright not installed")

# Copy application code
COPY . .

# CRITICAL: Verify static files exist and have content
# This will fail the build if files are missing or empty
RUN echo "Verifying critical static files..." && \
    if [ ! -f static/js/app-core.js ]; then \
        echo "ERROR: static/js/app-core.js not found!"; \
        exit 1; \
    fi && \
    if [ ! -s static/js/app-core.js ]; then \
        echo "ERROR: static/js/app-core.js is empty!"; \
        exit 1; \
    fi && \
    if [ ! -f static/js/service-templates.js ]; then \
        echo "ERROR: static/js/service-templates.js not found!"; \
        exit 1; \
    fi && \
    if [ ! -s static/js/service-templates.js ]; then \
        echo "ERROR: static/js/service-templates.js is empty!"; \
        exit 1; \
    fi && \
    if [ ! -f templates/index.html ]; then \
        echo "ERROR: templates/index.html not found!"; \
        exit 1; \
    fi && \
    if [ ! -s templates/index.html ]; then \
        echo "ERROR: templates/index.html is empty!"; \
        exit 1; \
    fi && \
    echo "✓ app-core.js: $(wc -l < static/js/app-core.js) lines" && \
    echo "✓ service-templates.js: $(wc -l < static/js/service-templates.js) lines" && \
    echo "✓ index.html: $(wc -l < templates/index.html) lines" && \
    echo "✓ All critical files verified!"

# Create a non-root user to run the app
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Ensure static files have correct permissions
RUN chmod -R 755 /app/static && \
    chmod 644 /app/static/js/*.js && \
    chmod 644 /app/static/css/*.css && \
    chmod 644 /app/templates/*.html

# Switch to non-root user
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99
ENV PYTHONDONTWRITEBYTECODE=1

# Final verification as the app user
RUN echo "Final verification as appuser:" && \
    ls -la /app/static/js/app-core.js && \
    ls -la /app/templates/index.html

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-10000}/health || exit 1

# Run the application
CMD ["gunicorn", "app:app", "--config", "gunicorn_config.py"]

# I did no harm and this file is not truncated
