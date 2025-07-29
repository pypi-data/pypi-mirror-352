class YOLODetector:
    def __init__(self, model_path):
        from ultralytics import YOLO
        self.model = YOLO(model_path)

    def detect(self, frame):
        results = self.model(frame)
        return results[0].boxes.data.cpu().numpy()
