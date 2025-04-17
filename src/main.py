import cv2
import redis
import base64
import numpy as np
from ultralytics import YOLO
from config.config import settings

if __name__ == "__main__":
    model = YOLO(settings.MODEL_PATH)
    redis_client = redis.Redis(
        host=settings.REDIS.HOST,
        port=settings.REDIS.PORT,
        password=settings.REDIS.PASSWORD
    )

    streams = redis_client.xread({"frame_stream": '0'}, block=0)
    for stream_name, entries in streams:
        for entry_id, data in entries:
            frame_buffer = base64.b64decode(data[b"frame"])
            frame = np.frombuffer(frame_buffer, np.uint8)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
