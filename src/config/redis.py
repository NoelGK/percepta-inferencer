import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()


@dataclass
class RedisConfig:
    HOST = os.getenv("REDIS_HOST")
    PORT = os.getenv("REDIS_PORT")
    PASSWORD = os.getenv("REDIS_PASSWORD")
