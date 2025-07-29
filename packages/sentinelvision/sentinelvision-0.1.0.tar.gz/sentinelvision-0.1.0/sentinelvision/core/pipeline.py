def run_pipeline(config_path=None):
    from .config import CONFIG
    from .detector import YOLODetector
    from .tracker import DeepSORTTracker
    from .pose import PoseEstimator
    from .llm_module import LLMModule
    from .prompt_builder import build_prompt
    import cv2
    import yaml

    if config_path:
        with open(config_path, 'r') as f:
            CONFIG.update(yaml.safe_load(f))

    detector = YOLODetector(CONFIG["YOLO_MODEL_PATH"])
    tracker = DeepSORTTracker()
    pose_estimator = PoseEstimator()
    llm = LLMModule()

    cap = cv2.VideoCapture(CONFIG["VIDEO_SOURCE"])

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        objects = detector.detect(frame)
        tracked_objects = tracker.update(objects, frame)
        poses = pose_estimator.estimate(frame)
        prompt = build_prompt(tracked_objects, poses)
        reasoning = llm.reason(prompt)

        print(reasoning)

        if CONFIG["DISPLAY"]:
            cv2.imshow("SentinelVision", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
