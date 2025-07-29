class PoseEstimator:
    def __init__(self):
        import mediapipe as mp
        self.pose = mp.solutions.pose.Pose()

    def estimate(self, frame):
        import cv2
        import mediapipe as mp
        results = self.pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        return results
