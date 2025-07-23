
import base64

import cv2


class Camera:
    def __init__(self, url: str):
        self.url = url
        self.last_image = None

    def get_camera_image_urls(self):
        # This method gets the current webcam image and returns it as URL Encoded image.
        cap = cv2.VideoCapture(self.url)
        ret, frame = cap.read()
        if ret:
            _, buffer = cv2.imencode('.jpg', frame)
            self.last_image = [f"data:image/jpeg;base64,{base64.b64encode(buffer).decode()}"]
            return self.last_image
        return []
