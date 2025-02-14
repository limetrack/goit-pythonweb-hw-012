import redis.asyncio as redis
from src.conf.config import app_config

# Initialize the Redis client using the configured Redis URL
redis_client = redis.Redis.from_url(app_config.REDIS_URL, decode_responses=True)


async def get_redis():
    """
    Get the Redis client instance.

    Returns:
        redis.Redis: The Redis client instance.
    """
    return redis_client
