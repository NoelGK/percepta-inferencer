import redis
from src.config.logging import appLogging as logging
from src.schemas.new_stream_schema import NewStreamSchema
from src.inference import InferencerThread

class ConsumerManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.consumers = {}

    def add_consumer(self, new_stream: NewStreamSchema):
        stream_name = f"frame_stream:{new_stream.device_id}"
        group_name = f"consumer:{new_stream.device_id}"
        try:
            self.redis_client.xgroup_create(
                name=stream_name,
                groupname=group_name,
                id='0',
                mkstream=True
            )
            self.consumer_groups[group_name] = stream_name
        except redis.exceptions.ResponseError:
            logging.warning(f"Consumer group {group_name} already exists")

        inference_thread = InferencerThread(self.redis_client, stream_name, group_name)
        self.inference_processes[stream_name] = inference_thread
        inference_thread.start()
        return stream_name

    def remove_consumer(self, stream_name: str) -> bool:
        try:
            self.consumers[stream_name].stop()
            self.consumers.pop(stream_name)
            return True
        except KeyError:
            logging.error(f"Tried to stop inference for stream {stream_name}, which is not in the active consumers")
            return False
