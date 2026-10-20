import time
import threading
from typing import Optional, Union

class VideoCamera:
    """
    Thread-safe OpenCV Camera Streamer.
    Supports Webcams, RTSP IP CCTV feeds, and video files with continuous looping.
    """
    def __init__(self, source: Union[int, str] = 0, target_size=(1280, 720)):
        self.source = source
        self.target_size = target_size
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.lock = threading.Lock()
        self.thread = None

        self._start_capture()

    def _start_capture(self):
        try:
            import cv2
            self.cap = cv2.VideoCapture(self.source)
            if self.cap.isOpened():
                self.is_running = True
                self.thread = threading.Thread(target=self._capture_loop, daemon=True)
                self.thread.start()
                print(f"[SUCCESS] Camera stream started for source: {self.source}")
            else:
                print(f"[WARNING] Unable to open camera source: {self.source}")
        except Exception as e:
            print(f"[ERROR] Camera initialization exception: {e}")

    def _capture_loop(self):
        import cv2
        while self.is_running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                if self.target_size:
                    frame = cv2.resize(frame, self.target_size)
                with self.lock:
                    self.current_frame = frame
            else:
                # If reading from a video file, loop back to beginning
                if isinstance(self.source, str) and not self.source.startswith("rtsp"):
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                else:
                    time.sleep(0.1)
            time.sleep(0.02) # ~30-40 FPS

    def read_frame(self):
        """Returns the latest captured OpenCV frame."""
        with self.lock:
            if self.current_frame is not None:
                return self.current_frame.copy()
        return None

    def get_jpeg_bytes(self) -> Optional[bytes]:
        """Encodes current frame as JPEG bytes for web streaming."""
        import cv2
        frame = self.read_frame()
        if frame is not None:
            ret, jpeg = cv2.imencode('.jpg', frame)
            if ret:
                return jpeg.tobytes()
        return None

    def stop(self):
        """Release camera and terminate capture loop."""
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
            self.cap = None
