import os
from dotenv import load_dotenv
from dataclasses import dataclass
from config.redis import RedisConfig

load_dotenv()


@dataclass
class Settings:
    REDIS: RedisConfig = RedisConfig()
    MODEL_PATH: str = os.getenv("MODEL_PATH", "yolo8s.pt")


settings = Settings()
