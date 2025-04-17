import os
from dotenv import load_dotenv
from dataclasses import dataclass, field
from config.redis import RedisConfig

load_dotenv()


@dataclass
class Settings:
    # Redis service configuration
    REDIS: RedisConfig = field(default_factory=RedisConfig)

    # Model configuration
    MODEL_NAME: str = os.getenv("MODEL_NAME", "yolov8s.pt")
    BATCH_SIZE = int(os.getenv("INFERENCE_BATCH_SIZE", 16))
    BATCH_TIMEOUT = float(os.getenv("INFERENCE_BATCH_TIMEOUT", 2.0))


settings = Settings()
