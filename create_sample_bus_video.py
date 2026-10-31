import os
import cv2
import numpy as np

def generate_terminal_video(output_path="sample_bus_terminal_stream.mp4", duration_sec=18, fps=25):
    width, height = 1280, 720
    total_frames = duration_sec * fps
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Load high-res real bus assets
    bus1_raw = cv2.imread("sample_bus_1_TN01AN2345.jpg")
    bus2_raw = cv2.imread("sample_bus_2_TN38N4567.jpg")
    
    if bus1_raw is None or bus2_raw is None:
        print("[ERROR] Sample bus images not found.")
        return

    # Realistic sizing for 1280x720 CCTV perspective
    b_w, b_h = 460, 310
    bus1 = cv2.resize(bus1_raw, (b_w, b_h))
    bus2 = cv2.resize(bus2_raw, (b_w, b_h))

    # Stamp sharp high-contrast Indian HSRP license plates on front bumpers
    # Bus 1 plate: TN 01 AN 2345
    p1_x1, p1_y1, p1_x2, p1_y2 = 100, 240, 280, 280
    cv2.rectangle(bus1, (p1_x1, p1_y1), (p1_x2, p1_y2), (255, 255, 255), -1)
    cv2.rectangle(bus1, (p1_x1, p1_y1), (p1_x2, p1_y2), (20, 20, 20), 2)
    # Blue IND strip on left
    cv2.rectangle(bus1, (p1_x1, p1_y1), (p1_x1 + 18, p1_y2), (220, 100, 20), -1)
    cv2.putText(bus1, "TN 01 AN 2345", (p1_x1 + 24, p1_y1 + 28), cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 0, 0), 2, cv2.LINE_AA)

    # Bus 2 plate: TN 38 N 4567
    p2_x1, p2_y1, p2_x2, p2_y2 = 130, 240, 310, 280
    cv2.rectangle(bus2, (p2_x1, p2_y1), (p2_x2, p2_y2), (255, 255, 255), -1)
    cv2.rectangle(bus2, (p2_x1, p2_y1), (p2_x2, p2_y2), (20, 20, 20), 2)
    # Blue IND strip on left
    cv2.rectangle(bus2, (p2_x1, p2_y1), (p2_x1 + 18, p2_y2), (220, 100, 20), -1)
    cv2.putText(bus2, "TN 38 N 4567", (p2_x1 + 24, p2_y1 + 28), cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 0, 0), 2, cv2.LINE_AA)

    # Create terminal background
    base_bg = np.zeros((height, width, 3), dtype=np.uint8)
    base_bg[:] = (48, 50, 54) # Asphalt tarmac
    
    # Platform pavement at top (y: 0 to 120)
    base_bg[0:120, :] = (165, 170, 175)
    # Yellow platform safety edge line
    cv2.line(base_bg, (0, 120), (width, 120), (0, 215, 255), 4)

    # Paint Bay Markings (B01, B02, B03, B04)
    bays = [
        ("B01", 30, 330),
        ("B02", 350, 650),
        ("B03", 670, 970),
        ("B04", 990, 1270)
    ]
    for name, x1, x2 in bays:
        # Yellow dashed parking lines
        for y in range(125, 660, 32):
            cv2.line(base_bg, (x1, y), (x1, min(660, y+18)), (0, 215, 255), 2)
            cv2.line(base_bg, (x2, y), (x2, min(660, y+18)), (0, 215, 255), 2)
        # Bay rear stop bar
        cv2.line(base_bg, (x1, 140), (x2, 140), (0, 215, 255), 3)
        # Bay Label painted on tarmac
        cv2.putText(base_bg, f"BAY {name}", (x1 + 75, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.95, (85, 90, 95), 2, cv2.LINE_AA)
        cv2.putText(base_bg, f"BAY {name}", (x1 + 75, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.93, (0, 215, 255), 1, cv2.LINE_AA)

    print(f"[INFO] Generating {total_frames} frames of terminal CCTV video...")

    # Trajectories:
    # Bus 1 targets Bay B02: docked position is (x=270, y=260) -> bottom_center = (500, 570) [inside Bay B02: x 350 to 650]
    b1_start_x, b1_start_y = 1100, 380
    b1_dock_x, b1_dock_y = 270, 260

    # Bus 2 targets Bay B03: docked position is (x=590, y=260) -> bottom_center = (820, 570) [inside Bay B03: x 670 to 970]
    b2_start_x, b2_start_y = 1150, 380
    b2_dock_x, b2_dock_y = 590, 260

    for f_idx in range(total_frames):
        frame = base_bg.copy()
        
        # 1. Bus 1 Movement (Frames 0 to 200)
        if f_idx < 100:
            prog = f_idx / 100.0
            ease = 1.0 - (1.0 - prog)**2
            b1_x = int(b1_start_x + (b1_dock_x - b1_start_x) * ease)
            b1_y = int(b1_start_y + (b1_dock_y - b1_start_y) * ease)
        else:
            b1_x = b1_dock_x
            b1_y = b1_dock_y
        
        # Overlay Bus 1
        y1, y2 = b1_y, b1_y + b_h
        x1, x2 = b1_x, b1_x + b_w
        if 0 <= y1 and y2 <= height and 0 <= x1 and x2 <= width:
            frame[y1:y2, x1:x2] = bus1

        # 2. Bus 2 Movement (Enters at frame 180)
        if f_idx >= 180:
            if f_idx < 290:
                b2_prog = (f_idx - 180) / 110.0
                ease2 = 1.0 - (1.0 - b2_prog)**2
                b2_x = int(b2_start_x + (b2_dock_x - b2_start_x) * ease2)
                b2_y = int(b2_start_y + (b2_dock_y - b2_start_y) * ease2)
            else:
                b2_x = b2_dock_x
                b2_y = b2_dock_y

            y1, y2 = b2_y, b2_y + b_h
            x1, x2 = b2_x, b2_x + b_w
            if 0 <= y1 and y2 <= height and 0 <= x1 and x2 <= width:
                frame[y1:y2, x1:x2] = bus2

        # 3. Terminal CCTV Overhead HUD
        # Top banner
        cv2.rectangle(frame, (0, 0), (width, 36), (15, 23, 42), -1)
        # Red REC indicator
        cv2.circle(frame, (24, 18), 6, (0, 0, 255), -1)
        cv2.putText(frame, "LIVE REC  CAM-01 [OVERHEAD TERMINAL BAYS B01-B04]", (40, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
        
        # Live timecode
        sec = f_idx // fps
        millis = int((f_idx % fps) * (1000 / fps))
        cv2.putText(frame, f"2026-11-01 12:45:{sec:02d}.{millis:03d} IST", (width - 260, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (148, 163, 184), 1, cv2.LINE_AA)

        out.write(frame)

    out.release()
    print(f"[SUCCESS] Video created successfully: {output_path} ({total_frames} frames)")

if __name__ == "__main__":
    generate_terminal_video()
