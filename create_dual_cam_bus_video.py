import os
import cv2
import numpy as np

def generate_dual_camera_video(output_path="dual_camera_smart_bus_system.mp4", duration_sec=22, fps=25):
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

    # Sizing for Top-View Camera (Left pane: 720 wide x 720 high)
    cam1_w, cam1_h = 740, 720
    b_top_w, b_top_h = 200, 310
    bus1_top = cv2.resize(bus1_raw, (b_top_w, b_top_h))
    bus2_top = cv2.resize(bus2_raw, (b_top_w, b_top_h))

    # Sizing for Front-View ANPR Camera (Right pane: 540 wide x 720 high)
    cam2_w, cam2_h = 540, 720
    b_front_w, b_front_h = 480, 340
    bus1_front = cv2.resize(bus1_raw, (b_front_w, b_front_h))
    bus2_front = cv2.resize(bus2_raw, (b_front_w, b_front_h))

    # Add ultra-sharp Indian HSRP license plate on front views
    # Bus 1: TN 01 AN 2345
    p1_x1, p1_y1, p1_x2, p1_y2 = 120, 260, 340, 305
    cv2.rectangle(bus1_front, (p1_x1, p1_y1), (p1_x2, p1_y2), (255, 255, 255), -1)
    cv2.rectangle(bus1_front, (p1_x1, p1_y1), (p1_x2, p1_y2), (20, 20, 20), 2)
    cv2.rectangle(bus1_front, (p1_x1, p1_y1), (p1_x1 + 22, p1_y2), (220, 100, 20), -1)
    cv2.putText(bus1_front, "TN 01 AN 2345", (p1_x1 + 30, p1_y1 + 32), cv2.FONT_HERSHEY_DUPLEX, 0.72, (0, 0, 0), 2, cv2.LINE_AA)

    # Bus 2: TN 38 N 4567
    p2_x1, p2_y1, p2_x2, p2_y2 = 140, 260, 360, 305
    cv2.rectangle(bus2_front, (p2_x1, p2_y1), (p2_x2, p2_y2), (255, 255, 255), -1)
    cv2.rectangle(bus2_front, (p2_x1, p2_y1), (p2_x2, p2_y2), (20, 20, 20), 2)
    cv2.rectangle(bus2_front, (p2_x1, p2_y1), (p2_x1 + 22, p2_y2), (220, 100, 20), -1)
    cv2.putText(bus2_front, "TN 38 N 4567", (p2_x1 + 30, p2_y1 + 32), cv2.FONT_HERSHEY_DUPLEX, 0.72, (0, 0, 0), 2, cv2.LINE_AA)

    # 1. Base Background for Left Pane (CAM-01: Top View Overhead Bays B01, B02, B03)
    cam1_bg = np.zeros((cam1_h, cam1_w, 3), dtype=np.uint8)
    cam1_bg[:] = (46, 48, 52) # Dark asphalt
    
    # Platform pavement at top (y: 0 to 110)
    cam1_bg[0:110, :] = (160, 165, 170)
    cv2.line(cam1_bg, (0, 110), (cam1_w, 110), (0, 215, 255), 4)

    # Define Three Bays: B01, B02, B03
    three_bays = [
        ("B01", 30, 250),
        ("B02", 265, 485),
        ("B03", 500, 720)
    ]

    for name, x1, x2 in three_bays:
        # Yellow dashed dividing lines
        for y in range(115, 680, 30):
            cv2.line(cam1_bg, (x1, y), (x1, min(680, y+16)), (0, 215, 255), 2)
            cv2.line(cam1_bg, (x2, y), (x2, min(680, y+16)), (0, 215, 255), 2)
        # Bay rear stop bar
        cv2.line(cam1_bg, (x1, 130), (x2, 130), (0, 215, 255), 3)
        # Bay Label painted on tarmac
        cv2.putText(cam1_bg, f"BAY {name}", (x1 + 35, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (75, 80, 85), 2, cv2.LINE_AA)
        cv2.putText(cam1_bg, f"BAY {name}", (x1 + 35, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.83, (0, 215, 255), 1, cv2.LINE_AA)

    # 2. Base Background for Right Pane (CAM-02: Front View ANPR)
    cam2_bg = np.zeros((cam2_h, cam2_w, 3), dtype=np.uint8)
    cam2_bg[:] = (28, 30, 36)

    print(f"[INFO] Rendering {total_frames} frames of dual-camera smart bus stand video...")

    # Trajectories for Top-View:
    # Bus 1 targets Bay B02: Docked position is (x=275, y=250)
    b1_start_x, b1_start_y = 650, 450
    b1_dock_x, b1_dock_y = 275, 250

    # Bus 2 targets Bay B03: Docked position is (x=510, y=250)
    b2_start_x, b2_start_y = 680, 450
    b2_dock_x, b2_dock_y = 510, 250

    # Timeline in Frames:
    # Frame 0 to 60 (t=0 to 2.4s): Terminal empty, all bays B01, B02, B03 empty
    # Frame 60 to 140 (t=2.4s to 5.6s): Bus 1 drives into Bay B02
    # Frame 140 to 265 (t=5.6s to 10.6s): Bus 1 STOPS in Bay B02. Holds for >5.0s (125 frames = 5.0 seconds!)
    # At Frame 265: Bus 1 completes 5.0s hold! Parked confirmed -> Plate TN 01 AN 2345 verified!
    # Frame 270 to 360 (t=10.8s to 14.4s): Bus 2 drives into Bay B03
    # Frame 360 to 485 (t=14.4s to 19.4s): Bus 2 STOPS in Bay B03. Holds for >5.0s (125 frames = 5.0 seconds!)
    # At Frame 485: Bus 2 completes 5.0s hold! Parked confirmed -> Plate TN 38 N 4567 verified!

    for f_idx in range(total_frames):
        full_frame = np.zeros((height, width, 3), dtype=np.uint8)
        left_pane = cam1_bg.copy()
        right_pane = cam2_bg.copy()

        # ==========================================
        # LEFT PANE: CAM-01 (Top-View Overhead Bays)
        # ==========================================
        # Bus 1 Motion
        if f_idx >= 50:
            if f_idx < 140:
                prog = (f_idx - 50) / 90.0
                ease = 1.0 - (1.0 - prog)**2
                b1_x = int(b1_start_x + (b1_dock_x - b1_start_x) * ease)
                b1_y = int(b1_start_y + (b1_dock_y - b1_start_y) * ease)
            else:
                b1_x = b1_dock_x
                b1_y = b1_dock_y

            y1, y2 = b1_y, b1_y + b_top_h
            x1, x2 = b1_x, b1_x + b_top_w
            if 0 <= y1 and y2 <= cam1_h and 0 <= x1 and x2 <= cam1_w:
                left_pane[y1:y2, x1:x2] = bus1_top

        # Bus 2 Motion
        if f_idx >= 270:
            if f_idx < 360:
                b2_prog = (f_idx - 270) / 90.0
                ease2 = 1.0 - (1.0 - b2_prog)**2
                b2_x = int(b2_start_x + (b2_dock_x - b2_start_x) * ease2)
                b2_y = int(b2_start_y + (b2_dock_y - b2_start_y) * ease2)
            else:
                b2_x = b2_dock_x
                b2_y = b2_dock_y

            y1, y2 = b2_y, b2_y + b_top_h
            x1, x2 = b2_x, b2_x + b_top_w
            if 0 <= y1 and y2 <= cam1_h and 0 <= x1 and x2 <= cam1_w:
                left_pane[y1:y2, x1:x2] = bus2_top

        # CAM-01 Header HUD
        cv2.rectangle(left_pane, (0, 0), (cam1_w, 36), (15, 23, 42), -1)
        cv2.circle(left_pane, (20, 18), 5, (0, 0, 255), -1)
        cv2.putText(left_pane, "CAM-01: OVERHEAD TOP VIEW (BAYS B01, B02, B03)", (34, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)
        
        # ==========================================
        # RIGHT PANE: CAM-02 (Front-View ANPR Camera)
        # ==========================================
        # Determine which bus front view to show based on confirmation stage
        if f_idx < 140:
            # Standby state
            cv2.putText(right_pane, "STANDBY: WAITING FOR DOCKING...", (cam2_w//2 - 180, cam2_h//2 - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.60, (148, 163, 184), 1, cv2.LINE_AA)
            cv2.putText(right_pane, "Top-View Cam must confirm 5s hold", (cam2_w//2 - 170, cam2_h//2 + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (100, 116, 139), 1, cv2.LINE_AA)
        
        elif f_idx >= 140 and f_idx < 270:
            # Bus 1 front view
            # Paste front view centered
            fy1, fy2 = 180, 180 + b_front_h
            fx1, fx2 = 30, 30 + b_front_w
            right_pane[fy1:fy2, fx1:fx2] = bus1_front

            # ANPR Status banner
            if f_idx < 265:
                dwell_sec = (f_idx - 140) / float(fps)
                cv2.rectangle(right_pane, (30, 540), (cam2_w - 30, 590), (15, 23, 42), -1)
                cv2.putText(right_pane, f"VERIFYING 5s DWELL HOLD: {dwell_sec:.1f}s / 5.0s", (45, 572), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 215, 255), 2, cv2.LINE_AA)
            else:
                cv2.rectangle(right_pane, (30, 540), (cam2_w - 30, 590), (16, 185, 129), -1)
                cv2.putText(right_pane, "PARKED CONFIRMED - ANPR: TN 01 AN 2345", (45, 572), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)

        elif f_idx >= 270:
            # Bus 2 front view
            fy1, fy2 = 180, 180 + b_front_h
            fx1, fx2 = 30, 30 + b_front_w
            right_pane[fy1:fy2, fx1:fx2] = bus2_front

            if f_idx < 485:
                if f_idx < 360:
                    cv2.rectangle(right_pane, (30, 540), (cam2_w - 30, 590), (15, 23, 42), -1)
                    cv2.putText(right_pane, "BUS 2 APPROACHING BAY B03...", (45, 572), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (56, 189, 248), 2, cv2.LINE_AA)
                else:
                    dwell2 = (f_idx - 360) / float(fps)
                    cv2.rectangle(right_pane, (30, 540), (cam2_w - 30, 590), (15, 23, 42), -1)
                    cv2.putText(right_pane, f"VERIFYING 5s DWELL HOLD: {dwell2:.1f}s / 5.0s", (45, 572), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 215, 255), 2, cv2.LINE_AA)
            else:
                cv2.rectangle(right_pane, (30, 540), (cam2_w - 30, 590), (16, 185, 129), -1)
                cv2.putText(right_pane, "PARKED CONFIRMED - ANPR: TN 38 N 4567", (45, 572), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)

        # CAM-02 Header HUD
        cv2.rectangle(right_pane, (0, 0), (cam2_w, 36), (15, 23, 42), -1)
        cv2.circle(right_pane, (20, 18), 5, (0, 200, 0), -1)
        cv2.putText(right_pane, "CAM-02: FRONT VIEW ANPR PLATE SENSOR", (34, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)

        # Combine Panes
        full_frame[:, 0:cam1_w] = left_pane
        full_frame[:, cam1_w:width] = right_pane

        # Vertical Divider
        cv2.line(full_frame, (cam1_w, 0), (cam1_w, height), (0, 215, 255), 3)

        out.write(full_frame)

    out.release()
    print(f"[SUCCESS] Dual-camera video created: {output_path} ({total_frames} frames)")

if __name__ == "__main__":
    generate_dual_camera_video()
