import os
from pathlib import Path

import pytest

from app.infraestructure.vision.plate_recognizer import PlateRecognizer


BASE_DIR = Path(__file__).parent
IMAGE_PATH = BASE_DIR / "test_images" / "coche.jpg"


@pytest.mark.skipif(
    os.environ.get("RUN_VISION_MODEL_TEST") != "1",
    reason="Set RUN_VISION_MODEL_TEST=1 to run the local YOLO plate model smoke test.",
)
def test_plate_recognizer_detects_from_sample_image():
    recognizer = PlateRecognizer()

    detections = recognizer.detect(
        image_path=str(IMAGE_PATH),
        save_result=True,
    )

    assert isinstance(detections, list)
