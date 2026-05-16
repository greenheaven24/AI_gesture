import cv2
import pyautogui
from hand_tracker import HandTracker
from gesture import detect_gesture
from cursor_control import CursorController

INDEX_TIP = 8  # landmark index for index fingertip


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam. Check it is connected and not in use.")

    cam_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cam_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    screen_w, screen_h = pyautogui.size()

    tracker = HandTracker()
    controller = CursorController(cam_w, cam_h, screen_w, screen_h, smoothing=7)

    print("Gesture controls:")
    print("  Index finger pointing   → move cursor")
    print("  Pinch (thumb+index)     → left click")
    print("  Peace sign (2 fingers)  → next slide  [→]")
    print("  Ring+pinky up           → prev slide  [←]")
    print("  Open palm               → scroll up")
    print("  Fist                    → scroll down")
    print("  Press Q in the window   → quit")

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        frame = tracker.find_hands(frame, draw=True)
        landmarks = tracker.get_landmarks(frame)
        gesture = detect_gesture(landmarks)

        if landmarks:
            tip = landmarks[INDEX_TIP]
            if gesture == 'move':
                controller.move(tip[0], tip[1])
            elif gesture == 'click':
                controller.move(tip[0], tip[1])
                controller.click()
            elif gesture == 'next_slide':
                controller.next_slide()
            elif gesture == 'prev_slide':
                controller.prev_slide()
            elif gesture == 'scroll_up':
                controller.scroll_up()
            elif gesture == 'scroll_down':
                controller.scroll_down()

        # Overlay gesture label on the camera feed
        label_color = {
            'move': (0, 255, 0),
            'click': (0, 200, 255),
            'next_slide': (255, 100, 0),
            'prev_slide': (255, 0, 100),
            'scroll_up': (200, 255, 0),
            'scroll_down': (0, 100, 255),
            'idle': (180, 180, 180),
        }.get(gesture, (255, 255, 255))

        cv2.putText(frame, f"Gesture: {gesture}", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, label_color, 2)

        cv2.imshow("Gesture Control (press Q to quit)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
