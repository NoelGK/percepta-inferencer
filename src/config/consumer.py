import redis
import redis.exceptions
from config.config import settings
from config.logging import logger

redis_client = redis.Redis(
    host=settings.REDIS.HOST,
    port=settings.REDIS.PORT,
    password=settings.REDIS.PASSWORD
)

FRAME_STREAM_NAME = "frame_stream"
CONSUMER_GROUP_NAME = "percepta.inference_group"
CONSUMER_NAME = "worker-1"

try:
    redis_client.xgroup_create(
        name=FRAME_STREAM_NAME,
        groupname=CONSUMER_GROUP_NAME,
        id='0',
        mkstream=True
    )
except redis.exceptions.ResponseError:
    logger.warning(f"Consumer group {CONSUMER_GROUP_NAME} already exists")
