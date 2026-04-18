import redis
from datetime import datetime
import logging
from fastapi import HTTPException
from .config import settings

# Initialize Redis client
r = redis.from_url(settings.redis_url, decode_responses=True)
logger = logging.getLogger(__name__)

def check_budget(user_id: str, estimated_cost: float = 0.0):
    """
    Checks if the user has enough monthly budget.
    Logic follow CODE_LAB Part 4 Exercise 4.4 and Part 6 Step 6.
    """
    try:
        month_key = datetime.now().strftime("%Y-%m")
        key = f"budget:{user_id}:{month_key}"
        
        current = float(r.get(key) or 0)
        
        if current + estimated_cost > settings.monthly_budget_usd:
            logger.warning(f"Budget exhausted for user {user_id}: {current} USD")
            raise HTTPException(
                status_code=402, 
                detail=f"Monthly budget exhausted. Limit: ${settings.monthly_budget_usd}"
            )
        
        # We don't increment here, we just check. 
        # The increment should happen after successful API call.
        return True
    
    except redis.RedisError as e:
        logger.error(f"Cost Guard Redis Error: {e}")
        return True # Fallback

def record_usage(user_id: str, prompt_tokens: int, completion_tokens: int):
    """
    Records the actual cost after a successful LLM call.
    Prices based on gpt-4o-mini estimates: 
    - Input: $0.150 / 1M tokens
    - Output: $0.600 / 1M tokens
    """
    try:
        month_key = datetime.now().strftime("%Y-%m")
        key = f"budget:{user_id}:{month_key}"
        
        cost = (prompt_tokens / 1000000) * 0.15 + (completion_tokens / 1000000) * 0.6
        
        r.incrbyfloat(key, cost)
        r.expire(key, 32 * 24 * 3600)  # TTL of 32 days
        
    except redis.RedisError as e:
        logger.error(f"Record usage Redis Error: {e}")
