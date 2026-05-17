from pathlib import Path
from ultralytics import YOLO


BASE_DIR = Path(__file__).parent

MODEL_PATH = BASE_DIR / "models" / "detectar_matriculas.pt"
RESULTS_DIR = BASE_DIR / "results"


class PlateRecognizer:
    def __init__(self):
        self.model = YOLO(str(MODEL_PATH))

    def detect(self, image_path: str, save_result: bool = True):
        """
        Detecta matrículas en una imagen.

        Si save_result=True, guarda una copia de la imagen con el recuadro
        de la matrícula dentro de app/infraestructure/vision/results/predict.
        """

        if save_result:
            results = self.model(
                image_path,
                save=True,
                project=str(RESULTS_DIR),
                name="predict",
                exist_ok=True
            )
        else:
            results = self.model(image_path)

        detections = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                detections.append({
                    "class": self.model.names[class_id],
                    "confidence": round(confidence, 4),
                    "bbox": {
                        "x1": round(x1, 2),
                        "y1": round(y1, 2),
                        "x2": round(x2, 2),
                        "y2": round(y2, 2),
                    }
                })

        return detections