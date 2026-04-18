import time
import redis
from fastapi import HTTPException
from .config import settings

# Initialize Redis client for internal logic
r = redis.from_url(settings.redis_url, decode_responses=True)

def check_rate_limit(user_id: str):
    """
    Implements a sliding window rate limiter using Redis.
    Limits to settings.rate_limit_per_minute requests per minute.
    """
    try:
        now = time.time()
        key = f"rate_limit:{user_id}"
        
        # Remove old requests from the window
        r.zremrangebyscore(key, 0, now - 60)
        
        # Count current requests
        request_count = r.zcard(key)
        
        if request_count >= settings.rate_limit_per_minute:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {settings.rate_limit_per_minute} req/min",
                headers={"Retry-After": "60"},
            )
            
        # Record new request
        r.zadd(key, {str(now): now})
        r.expire(key, 60)
        
    except redis.RedisError as e:
        # Fallback if Redis is down (optional decision: allow or deny?)
        # For this lab, we log it and allow to pass to avoid total outage
        import logging
        logging.getLogger(__name__).error(f"Redis Rate Limiter Error: {e}")
        pass
