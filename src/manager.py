import time
import redis
from typing import List
from config.logging import appLogging as logging
from schemas.new_stream_schema import NewStreamSchema
from inference import InferencerThread

class ConsumerManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.consumers = {}

    def add_consumer(self, new_stream: NewStreamSchema):
        stream_name, group_name = self.__consumer_names(new_stream.device_id)
        try:
            self.redis_client.xgroup_create(
                name=stream_name,
                groupname=group_name,
                id='0',
                mkstream=True
            )
        except redis.exceptions.ResponseError:
            logging.warning(f"Consumer group {stream_name} already exists")

        inference_thread = InferencerThread(self.redis_client, stream_name, group_name)
        self.consumers[stream_name] = inference_thread
        inference_thread.start()
        logging.info(f"Created inference consumer {group_name}")
        return stream_name

    def remove_consumer(self, device_id: str) -> bool:
        stream_name, group_name = self.__consumer_names(device_id)
        try:
            self.consumers[stream_name].stop()
            time.sleep(2)  # Timeout to fully stop inference thread

            self.consumers.pop(stream_name)
            self.redis_client.xgroup_destroy(stream_name, group_name)
            return True
        except KeyError:
            logging.error(f"Tried to stop inference for stream {stream_name}, which is not in the active consumers")
            return False

    def get_active_consumers(self) -> List:
        return [stream_name for stream_name in self.consumers]

    @staticmethod
    def __consumer_names(device_id):
        stream_name = f"frame_stream:{device_id}"
        group_name = f"consumer:{device_id}"
        return stream_name, group_name
