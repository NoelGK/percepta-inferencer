import redis
from src.config.logging import appLogging as logging
from src.schemas.new_stream_schema import NewStreamSchema
from src.inference import InferencerThread

class InferenceManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.consumer_groups = {}
        self.inference_processes = {}

    def add_consumer_group(self, new_stream: NewStreamSchema):
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
        self.inference_processes[stream_name] = inference_thread.start()
