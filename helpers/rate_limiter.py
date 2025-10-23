# helpers/rate_limiter.py
"""
Rate Limiter Helper for ScrapingBee YouTube Service
Date: October 23, 2025
Version: 1.0.0

Simple rate limiting to protect your 100K ScrapingBee credits.
No external dependencies required - uses in-memory storage.

USAGE:
    from helpers.rate_limiter import check_rate_limit
    
    # In your route:
    rate_check = check_rate_limit(request.remote_addr, limit_per_hour=20)
    if not rate_check['allowed']:
        return jsonify({'error': 'Rate limit exceeded'}), 429

Save as: helpers/rate_limiter.py (create helpers/ folder if needed)
"""

from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict
import threading

# Thread-safe storage for rate limits
_rate_limit_lock = threading.Lock()
_rate_limits = defaultdict(lambda: {'count': 0, 'reset_time': datetime.now()})


def check_rate_limit(identifier: str, limit_per_hour: int = 20) -> Dict:
    """
    Check if identifier (IP address or user ID) has exceeded rate limit
    
    Args:
        identifier: IP address or user identifier
        limit_per_hour: Maximum requests allowed per hour (default: 20)
        
    Returns:
        Dict with 'allowed' (bool) and additional info
    """
    with _rate_limit_lock:
        now = datetime.now()
        user_data = _rate_limits[identifier]
        
        # Reset if hour has passed
        if now >= user_data['reset_time']:
            user_data['count'] = 0
            user_data['reset_time'] = now + timedelta(hours=1)
        
        # Check if limit exceeded
        if user_data['count'] >= limit_per_hour:
            minutes_remaining = int((user_data['reset_time'] - now).total_seconds() / 60)
            return {
                'allowed': False,
                'limit': limit_per_hour,
                'current': user_data['count'],
                'reset_in_minutes': minutes_remaining,
                'reset_time': user_data['reset_time'].isoformat(),
                'message': f'Rate limit exceeded. Try again in {minutes_remaining} minutes.'
            }
        
        # Increment counter and allow
        user_data['count'] += 1
        remaining = limit_per_hour - user_data['count']
        
        return {
            'allowed': True,
            'limit': limit_per_hour,
            'current': user_data['count'],
            'remaining': remaining,
            'reset_time': user_data['reset_time'].isoformat(),
            'message': f'{remaining} requests remaining this hour'
        }


def get_rate_limit_status(identifier: str, limit_per_hour: int = 20) -> Dict:
    """Get current rate limit status without incrementing counter"""
    with _rate_limit_lock:
        now = datetime.now()
        user_data = _rate_limits[identifier]
        
        if now >= user_data['reset_time']:
            return {
                'current': 0,
                'limit': limit_per_hour,
                'remaining': limit_per_hour,
                'reset_in_minutes': 0,
                'message': 'No requests made in current period'
            }
        
        remaining = max(0, limit_per_hour - user_data['count'])
        minutes_remaining = int((user_data['reset_time'] - now).total_seconds() / 60)
        
        return {
            'current': user_data['count'],
            'limit': limit_per_hour,
            'remaining': remaining,
            'reset_in_minutes': minutes_remaining,
            'reset_time': user_data['reset_time'].isoformat(),
            'message': f'{remaining} requests remaining this hour'
        }


# This file is not truncated
