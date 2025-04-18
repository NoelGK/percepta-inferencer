from pathlib import Path
from typing import List
from ultralytics import YOLO
from config.logging import appLogging as logging
from config.config import settings


project_root = Path(__file__).resolve().parents[1]
model_path = project_root / "models" / settings.MODEL_NAME
MODEL = YOLO(model_path)


def process_batch(batch: List):
    results = MODEL(batch)
    for i, result in enumerate(results):
        class_names = [MODEL.names[int(cls_id)] for cls_id in result.boxes.cls]
    return class_names
