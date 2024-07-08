import sys

import cv2


def process_frame(frame, algorithm=None):
    if algorithm is None:
        return frame

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (0, 0), 5)
    return blur


def main():
    camera_id = 0
    delay = 1
    window_name = "video_capture"

    cap = cv2.VideoCapture(camera_id)

    if not cap.isOpened():
        sys.exit()

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to read frame")
            continue

        result = process_frame(
            frame=frame,
            algorithm=None,
        )

        cv2.imshow(window_name, result)
        if cv2.waitKey(delay) & 0xFF == ord("q"):
            break

    cv2.destroyWindow(window_name)


if __name__ == "__main__":
    main()
