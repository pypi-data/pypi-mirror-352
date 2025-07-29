import os
import logging
from leakybucket import (
    LeakyBucket,
    AsyncLeakyBucket
)
from leakybucket.persistence import (
    InMemoryLeakyBucketStorage,
    RedisLeakyBucketStorage
)
from dotenv import load_dotenv

_logger = logging.getLogger(__name__)

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
CLIENT_ID = os.getenv("ICONIC_CLIENT_ID")
MAX_RATE = 30 # max requests
TIME_PERIOD = 1 # per second

if REDIS_URL:
    try:
        from redis import Redis
        redis_client = Redis.from_url(REDIS_URL)
        storage = RedisLeakyBucketStorage(
            redis_client, 
            key_prefix=f"iconic_api_throttler:{CLIENT_ID}",
            max_rate=MAX_RATE,
            time_period=TIME_PERIOD
        )
    except ImportError:
        _logger.warning("Redis not installed. Falling back to InMemoryStorage for rate limiting. "
                        "Run 'pip install iconic-api-client[redis]' to use Redis.")
        storage = InMemoryLeakyBucketStorage(
            max_rate=MAX_RATE,
            time_period=TIME_PERIOD
        )
else:
    storage = InMemoryLeakyBucketStorage(
        max_rate=MAX_RATE, 
        time_period=TIME_PERIOD
    )
    
throttler = LeakyBucket(storage)
async_throttler = AsyncLeakyBucket(storage)