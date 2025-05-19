import cv2
import time
import redis
import base64
import threading
from pathlib import Path
from typing import List
import numpy as np
from ultralytics import YOLO
from config.logging import appLogging as logging
from config.config import settings


project_root = Path(__file__).resolve().parents[1]
model_path = project_root / "models" / settings.MODEL_NAME
MODEL = YOLO(model_path)


class InferencerThread(threading.Thread):
    def __init__(
        self, 
        redis_client: redis.Redis, 
        stream_name: str, 
        group_name: str
    ):
        super().__init__()
        self.redis_client = redis_client
        self.stream_name = stream_name
        self.group_name = group_name
        self.running: bool = True

    def run(self):
        frame_batch = []
        entry_ids = []
        last_batch_time = time.time()

        for streams in self.__stream_batch():
            for stream_name, entries in streams:
                for entry_id, data in entries:
                    try:
                        frame = self.__decode_frame(data)
                        self.frame_batch.append(frame)
                        self.entry_ids.append(entry_id)

                    except Exception as e:
                        logging.error(f"Failed to process entry {entry_id}:\n {e}")

            if frame_batch and (len(frame_batch) >= settings.BATCH_SIZE or time.time() - last_batch_time > settings.BATCH_TIMEOUT):
                try:
                    self.__process_batch(frame_batch)
                    self.redis_client.xack(self.stream_name, self.group_name, *entry_ids)

                except Exception as e:
                    logging.error(f"Error running inference over batch {self.entry_ids}:\n {e}")

                finally:
                    stream_name.clear()
                    entry_ids.clear()
                    last_batch_time = time.time()

    def stop(self):
        logging.info(f"Stopping inference thread for stream {self.stream_name}")
        self.running = False

    def __stream_batch(self, count: int = 1, block: int = 5000):
        """
            Calls the xreadgroup method over 'client' and yields 
            the stream returned.
        """
        while self.running:
            try:
                streams = self.redis_client.xreadgroup(
                    groupname=self.group_name,
                    consumername=self.group_name,
                    streams={self.stream_name: '>'},
                    count=count,
                    block=block
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

    @staticmethod
    def __decode_frame(data):
        frame_buffer = base64.b64decode(data[b"frame"])
        frame_array = np.frombuffer(frame_buffer, np.uint8)
        return cv2.imdecode(frame_array, cv2.IMREAD_COLOR)

    @staticmethod
    def __process_batch(batch: List):
        results = MODEL(batch)
        for i, result in enumerate(results):
            class_names = [MODEL.names[int(cls_id)] for cls_id in result.boxes.cls]
        return class_names
