from pathlib import Path
from plate_recognizer import PlateRecognizer


BASE_DIR = Path(__file__).parent
IMAGE_PATH = BASE_DIR / "test_images" / "coche.jpg"

recognizer = PlateRecognizer()

detections = recognizer.detect(
    image_path=str(IMAGE_PATH),
    save_result=True
)

print(detections)
print("Imagen con detección guardada en:")
print(BASE_DIR / "results" / "predict")