import time
import redis
import redis.exceptions
from config.config import settings
from config.logging import appLogging as logging

FRAME_STREAM_NAME = "frame_stream"
CONSUMER_GROUP_NAME = "percepta.inference_group"
CONSUMER_NAME = "worker-1"

redis_client = redis.Redis(
    host=settings.REDIS.HOST,
    port=settings.REDIS.PORT,
    password=settings.REDIS.PASSWORD
)
logging.info(f"Connected to Redis Stream '{FRAME_STREAM_NAME}' with group {CONSUMER_GROUP_NAME}")

try:
    redis_client.xgroup_create(
        name=FRAME_STREAM_NAME,
        groupname=CONSUMER_GROUP_NAME,
        id='0',
        mkstream=True
    )
except redis.exceptions.ResponseError:
    logging.warning(f"Consumer group {CONSUMER_GROUP_NAME} already exists")


def stream_batch(
    client: redis.Redis, 
    group_name: str = CONSUMER_GROUP_NAME,
    stream_name: str = FRAME_STREAM_NAME,
    count: int = 1,
    block: int = 5000
):
    """
        Calls the xreadgroup method over 'client' and yields 
        the stream returned.
    """
    while True:
        try:
            streams = redis_client.xreadgroup(
                groupname=CONSUMER_GROUP_NAME,
                consumername=CONSUMER_NAME,
                streams={FRAME_STREAM_NAME: '>'},
                count=1,
                block=5000
            )
            yield streams

        except redis.exceptions.ConnectionError as e:
            logging.error(f"Redis connection error:\n {e}")
            logging.info("Retrying in 5s...")
            time.sleep(5)

        except Exception as e:
            logging.error(f"Error reading from Redis Stream:\n {e}")
            logging.info(f"Re-starting connection in 5s...")
            time.sleep(5)
