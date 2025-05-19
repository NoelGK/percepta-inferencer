import redis
from typing import List
from fastapi import FastAPI, APIRouter
from manager import ConsumerManager
from config.config import settings
from config.logging import appLogging as logging
from schemas.new_stream_schema import NewStreamSchema

logging.info(f"Initializing inference pipeline...")
redis_client = redis.Redis(
    host=settings.REDIS.HOST,
    port=settings.REDIS.PORT,
    password=settings.REDIS.PASSWORD
)
logging.info(f"Connected to Redis at {settings.REDIS.HOST}")

manager = ConsumerManager(redis_client)
logging.info("Consumer manager initialized")

# API router and endpoints
router = APIRouter(prefix="/api/v1", tags=["Base"])


@router.post("/add-consumer", status_code=200)
def add_stream(new_stream: NewStreamSchema) -> str:
    new_stream_name = manager.add_consumer(new_stream)
    return new_stream_name


@router.delete("/remove-stream/{device_id}", status_code=200)
def stop_stream(device_id: str) -> bool:
    return manager.remove_consumer(device_id)


@router.get("/active-consumers", status_code=200)
def active_consumers() -> List:
    return manager.get_active_consumers()


api = FastAPI(
    title="Percepta Inference manager API",
    description="API for managing CV processing of frames from Redis Streams.",
    version="1.0.0",
    docs_url="/docs",           # Swagger UI
    redoc_url="/redoc",         # ReDoc alternative
    openapi_url="/openapi.json" # OpenAPI schema
)
api.include_router(router)
logging.info(f"Stream management API initialized")
