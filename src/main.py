import cv2
import time
import base64
import numpy as np
from inference import process_batch
from config.logging import logger
from config.config import settings
from config.consumer import (
    redis_client, 
    FRAME_STREAM_NAME, 
    CONSUMER_GROUP_NAME,
    CONSUMER_NAME
)


def decode_frame(data):
    frame_buffer = base64.b64decode(data[b"frame"])
    frame_array = np.frombuffer(frame_buffer, np.uint8)
    return cv2.imdecode(frame_array, cv2.IMREAD_COLOR)


def main():
    streams = redis_client.xreadgroup(
        groupname=CONSUMER_GROUP_NAME,
        consumername=CONSUMER_NAME,
        streams={FRAME_STREAM_NAME: '>'},
        count=1,
        block=5000
    )

    batch = []
    entry_ids = []
    last_batch_time = time.time()

    for stream_name, entries in streams:
        for entry_id, data in entries:
            try:
                frame = decode_frame(data)
                batch.append(frame)
                entry_ids.append(entry_id)

            except Exception as e:
                logger.error(f"Failed to process entry {entry_id}:\n {e}")

    if batch and (len(batch) >= settings.BATCH_SIZE or time.time() - last_batch_time > settings.BATCH_TIMEOUT):
        try:
            process_batch(batch, entry_ids, last_batch_time)
            redis_client.xack(FRAME_STREAM_NAME, CONSUMER_GROUP_NAME, *entry_ids)

        except Exception as e:
            logger.error(f"Error running inference over batch {entry_ids}:\n {e}")

        finally:
            batch.clear()
            entry_ids.clear()
            last_batch_time = time.time()


if __name__ == "__main__":
    main()
