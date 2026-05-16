import os
import urllib.request
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# MediaPipe gives us 21 landmark points per hand
# Key landmarks we use:
#   4  = thumb tip
#   8  = index finger tip
#   12 = middle finger tip
#   16 = ring finger tip
#   20 = pinky tip

MODEL_PATH = "hand_landmarker.task"
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)

_HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),         # index
    (0, 9), (9, 10), (10, 11), (11, 12),    # middle
    (0, 13), (13, 14), (14, 15), (15, 16),  # ring
    (0, 17), (17, 18), (18, 19), (19, 20),  # pinky
    (5, 9), (9, 13), (13, 17),              # palm
]


class HandTracker:
    def __init__(self, max_hands=1, detection_confidence=0.8, tracking_confidence=0.8):
        if not os.path.exists(MODEL_PATH):
            print("Downloading hand landmark model (~8 MB)...")
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
            print("Model ready.")

        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_confidence,
            min_hand_presence_confidence=tracking_confidence,
            min_tracking_confidence=tracking_confidence,
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self._results = None

    def find_hands(self, frame, draw=True):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        self._results = self.detector.detect(mp_image)

        if draw and self._results.hand_landmarks:
            h, w = frame.shape[:2]
            for hand_landmarks in self._results.hand_landmarks:
                pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]
                for a, b in _HAND_CONNECTIONS:
                    cv2.line(frame, pts[a], pts[b], (0, 220, 0), 2)
                for pt in pts:
                    cv2.circle(frame, pt, 5, (255, 255, 255), -1)
        return frame

    def get_landmarks(self, frame):
        """Return list of (x, y) pixel positions for each landmark, or None."""
        if not self._results or not self._results.hand_landmarks:
            return None
        h, w = frame.shape[:2]
        return [(int(lm.x * w), int(lm.y * h)) for lm in self._results.hand_landmarks[0]]
