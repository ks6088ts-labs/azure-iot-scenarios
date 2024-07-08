import cv2


def capture_image(camera_index: int) -> bytes:
    camera = cv2.VideoCapture(
        index=camera_index,
    )  # 0 is the camera index, it can be changed to the camera index of your camera
    return_value, image = camera.read()
    del camera
    if not return_value:
        raise Exception("Error capturing image")
    return cv2.imencode(".jpg", image)[1].tobytes()


if __name__ == "__main__":
    data = capture_image(
        camera_index=0,
    )
    with open("image.jpg", "wb") as f:
        f.write(data)
