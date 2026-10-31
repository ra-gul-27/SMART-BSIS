import cv2

def extract_clip():
    src = "real_bus_station_cctv.webm"
    dst = "real_bus_station_cctv.mp4"
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        print(f"Failed to open {src}")
        return

    start_frame = 1250
    end_frame = 1850
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(dst, fourcc, fps, (width, height))

    print(f"Extracting {end_frame - start_frame} frames ({width}x{height} @ {fps:.1f} FPS) from {src} to {dst}...")

    count = 0
    while cap.isOpened() and cap.get(cv2.CAP_PROP_POS_FRAMES) <= end_frame:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        count += 1

    cap.release()
    out.release()
    print(f"[SUCCESS] Exported {count} frames to {dst}!")

if __name__ == "__main__":
    extract_clip()
