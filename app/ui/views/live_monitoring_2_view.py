import os
import sys
import threading
import tkinter.filedialog as filedialog
import customtkinter as ctk
import cv2
from PIL import Image
from app.constants import COLORS, FONTS
from app.db.database import get_connection

# Add project root and backend to path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from backend.vision.video_pipeline import VideoAnalyticsEngine

class LiveMonitoring2View(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.app_controller = app_controller
        
        self.grid_columnconfigure(0, weight=1)

        self.current_bus_list = [
            "TN 01 AN 2345", 
            "TN 38 N 4567", 
            "TN 01 AB 1234", 
            "TN 02 XY 9876", 
            "TN 05 XY 7788", 
            "TN 43 B 1284"
        ]
        self.selected_bus = "TN 01 AN 2345"
        self.is_detecting = False
        self.is_auto_streaming = False
        self._stream_timer = None
        self._sample_cycle_idx = 0

        # Video Engine State
        self.video_engine = VideoAnalyticsEngine()
        self.video_engine.register_callback(self._on_video_detection_event)
        self.is_video_streaming = False
        self._video_timer = None
        self.active_video_source = "sample_bus_terminal_stream.mp4"

        self.video_label = None
        self.manifest_container = None
        self.ai_card_container = None
        self.timeline_list_container = None

        self._build_header()
        self._build_reviewer_demo_bar()
        self._build_content()
        self._refresh_all_data()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 12))
        header_frame.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header_frame, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")

        # Back button
        back_btn = ctk.CTkButton(
            left, text="← Back to Camera Grid", font=FONTS["label_md"], 
            fg_color="transparent", text_color=COLORS["on_surface_variant"], hover_color=COLORS["surface_variant"],
            command=lambda: self.app_controller.show_view("LiveMonitoring1"), anchor="w"
        )
        back_btn.pack(anchor="w", pady=(0, 4))
        
        ctk.CTkLabel(
            left, text="Real-Time AI Vision: YOLOv11 + ANPR Video Terminal Stream", font=FONTS["headline_lg"], text_color=COLORS["on_surface"]
        ).pack(anchor="w")

        right = ctk.CTkFrame(header_frame, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")
        
        # Vehicle Dropdown
        ctk.CTkLabel(right, text="Vehicle:", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(side="left", padx=(0, 4))
        self.bus_dropdown = ctk.CTkOptionMenu(
            right, values=self.current_bus_list, font=FONTS["data_mono"],
            fg_color=COLORS["surface_container_low"], text_color=COLORS["on_surface"],
            button_color=COLORS["surface_container_high"], button_hover_color=COLORS["outline_variant"],
            command=self._on_bus_select, width=145, height=36
        )
        self.bus_dropdown.pack(side="left", padx=(0, 6))
        self.bus_dropdown.set(self.selected_bus)

        # Upload Photo Button
        self.upload_btn = ctk.CTkButton(
            right, text="📷 Upload Photo...", font=FONTS["label_md"], height=36,
            fg_color=COLORS["surface_container_high"], text_color=COLORS["on_surface"],
            border_color=COLORS["outline_variant"], border_width=1, hover_color=COLORS["surface_container_highest"],
            command=self._load_custom_image
        )
        self.upload_btn.pack(side="left", padx=4)

        # Manual Refresh
        self.refresh_btn = ctk.CTkButton(
            right, text="🔄 Refresh", font=FONTS["label_md"], height=36,
            fg_color=COLORS["surface_container_high"], text_color=COLORS["primary"],
            border_color=COLORS["outline_variant"], border_width=1, hover_color=COLORS["surface_container_highest"],
            command=self._refresh_all_data
        )
        self.refresh_btn.pack(side="left", padx=4)

        # Single Run AI Detection
        self.detect_btn = ctk.CTkButton(
            right, text="⚡ Run Photo AI", font=FONTS["label_md"], height=36,
            fg_color=COLORS["primary"], text_color=COLORS["on_primary"], hover_color=COLORS["primary_container"],
            command=lambda: self._trigger_ai_detection()
        )
        self.detect_btn.pack(side="left", padx=4)

    def _build_reviewer_demo_bar(self):
        """Prominent dual-mode demonstration bar supporting both Live Video Stream and Real Bus Photo Analysis."""
        demo_card = ctk.CTkFrame(
            self, 
            fg_color="#eff6ff", 
            border_color="#0284c7", 
            border_width=2, 
            corner_radius=12
        )
        demo_card.grid(row=1, column=0, sticky="ew", padx=32, pady=(0, 16))

        inner = ctk.CTkFrame(demo_card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        # Header of Demo Card
        top_line = ctk.CTkFrame(inner, fg_color="transparent")
        top_line.pack(fill="x", pady=(0, 8))

        tag = ctk.CTkFrame(top_line, fg_color="#0284c7", corner_radius=6)
        tag.pack(side="left")
        ctk.CTkLabel(tag, text="★ TWO-CAMERA INTELLIGENT SYSTEM (BAYS B01, B02, B03)", font=("Inter", 10, "bold"), text_color="#ffffff").pack(padx=8, pady=2)

        ctk.CTkLabel(
            top_line, 
            text="CAM-01 (Top-View) verifies 5-second dwell hold (Red -> Green); CAM-02 (Front-View) then triggers ANPR plate detection:", 
            font=("Inter", 11, "bold"), 
            text_color="#0f172a"
        ).pack(side="left", padx=12)

        # Row 1: Real-Time Video Stream Controls
        v_row = ctk.CTkFrame(inner, fg_color="transparent")
        v_row.pack(fill="x", pady=(0, 6))
        v_row.grid_columnconfigure(0, weight=3)
        v_row.grid_columnconfigure(1, weight=2)
        v_row.grid_columnconfigure(2, weight=2)
        v_row.grid_columnconfigure(3, weight=1)
        v_row.grid_columnconfigure(4, weight=1)
        v_row.grid_columnconfigure(5, weight=1)

        # Button 1: Two-Camera Intelligent Stream (Top-View Bays B01, B02, B03 with 5s hold + Front ANPR)
        self.dual_cam_btn = ctk.CTkButton(
            v_row, 
            text="🎬 Two-Camera 5s Hold Stream\n(CAM-01 Top B01-B03 Red->Green + CAM-02 Front ANPR)", 
            font=("Inter", 11, "bold"), height=46,
            fg_color="#059669", hover_color="#047857", text_color="#ffffff",
            command=self._start_dual_camera_stream
        )
        self.dual_cam_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        # Button 2: Real Bus Station Video (KSRTC Davanagere Footage)
        self.real_footage_btn = ctk.CTkButton(
            v_row, 
            text="🎥 Real KSRTC Bus CCTV\n(Actual Terminal Footage)", 
            font=("Inter", 11, "bold"), height=46,
            fg_color="#0284c7", hover_color="#0369a1", text_color="#ffffff",
            command=self._start_real_footage_stream
        )
        self.real_footage_btn.grid(row=0, column=1, sticky="ew", padx=4)

        # Button 3: Upload Custom Video File
        self.upload_video_btn = ctk.CTkButton(
            v_row, 
            text="📁 Upload Video File...\n(Browse .mp4/.avi on disk)", 
            font=("Inter", 11, "bold"), height=46,
            fg_color=COLORS["surface_container_lowest"], border_color="#0284c7", border_width=1,
            hover_color=COLORS["surface_container_high"], text_color="#0284c7",
            command=self._load_custom_video
        )
        self.upload_video_btn.grid(row=0, column=2, sticky="ew", padx=4)

        # Button 4: Live Webcam Feed
        self.webcam_btn = ctk.CTkButton(
            v_row, 
            text="📹 Webcam\n(Camera 0)", 
            font=("Inter", 11, "bold"), height=46,
            fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1,
            hover_color=COLORS["surface_container_high"], text_color=COLORS["on_surface"],
            command=self._start_webcam_stream
        )
        self.webcam_btn.grid(row=0, column=3, sticky="ew", padx=4)

        # Button 5: Pause / Resume Stream
        self.pause_resume_btn = ctk.CTkButton(
            v_row, 
            text="⏸ Pause", 
            font=("Inter", 11, "bold"), height=46,
            fg_color="#b45309", hover_color="#92400e", text_color="#ffffff",
            command=self._pause_video_stream
        )
        self.pause_resume_btn.grid(row=0, column=4, sticky="ew", padx=4)

        # Button 6: Stop Video Stream
        self.stop_video_btn = ctk.CTkButton(
            v_row, 
            text="⏹ Stop", 
            font=("Inter", 11, "bold"), height=46,
            fg_color="#dc2626", hover_color="#b91c1c", text_color="#ffffff",
            command=self._stop_video_stream
        )
        self.stop_video_btn.grid(row=0, column=5, sticky="ew", padx=(4, 0))

        # Row 2: Secondary Photo Test Bar
        p_row = ctk.CTkFrame(inner, fg_color="#f8fafc", corner_radius=8)
        p_row.pack(fill="x", pady=(4, 0))
        p_row_inner = ctk.CTkFrame(p_row, fg_color="transparent")
        p_row_inner.pack(fill="x", padx=8, pady=4)

        ctk.CTkLabel(p_row_inner, text="Static Photo Mode:", font=("Inter", 10, "bold"), text_color=COLORS["on_surface_variant"]).pack(side="left", padx=(4, 8))

        ctk.CTkButton(
            p_row_inner, text="🚌 Photo 1 (Volvo AC)", font=("Inter", 10), height=28,
            fg_color="transparent", text_color="#1d4ed8", hover_color="#e0e7ff",
            command=lambda: self._test_sample_image("sample_bus_1_TN01AN2345.jpg", "TN 01 AN 2345")
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            p_row_inner, text="🚍 Photo 2 (Deluxe)", font=("Inter", 10), height=28,
            fg_color="transparent", text_color="#b45309", hover_color="#fef3c7",
            command=lambda: self._test_sample_image("sample_bus_2_TN38N4567.jpg", "TN 38 N 4567")
        ).pack(side="left", padx=4)

        self.cycle_btn = ctk.CTkButton(
            p_row_inner, text="🔄 Auto-Cycle Photos", font=("Inter", 10), height=28,
            fg_color="transparent", text_color="#059669", hover_color="#dcfce7",
            command=self._toggle_auto_stream
        )
        self.cycle_btn.pack(side="left", padx=4)

    def _start_dual_camera_stream(self):
        """Streams the synchronized two-camera system (Top-View Bays B01, B02, B03 with 5s hold + Front ANPR)."""
        video_file = "dual_camera_smart_bus_system.mp4"
        if not os.path.exists(video_file):
            try:
                import create_dual_cam_bus_video
                create_dual_cam_bus_video.generate_dual_camera_video(video_file)
            except Exception as e:
                print(f"Error generating dual camera video: {e}")
        self._start_video_stream_source(video_file)

    def _start_real_footage_stream(self):
        """Streams actual KSRTC bus station video footage (Davanagere Terminal)."""
        video_file = "real_bus_station_cctv.mp4"
        if not os.path.exists(video_file):
            video_file = "real_bus_station_cctv.webm"
        if os.path.exists(video_file):
            self._start_video_stream_source(video_file)
        else:
            print("[NOTICE] Real bus station video file not found on disk.")

    def _start_sample_video_stream(self):
        """Streams the realistic synthetic terminal CCTV video with real bus docking."""
        video_file = "sample_bus_terminal_stream.mp4"
        if not os.path.exists(video_file):
            try:
                import create_sample_bus_video
                create_sample_bus_video.generate_terminal_video(video_file)
            except Exception as e:
                print(f"Error generating sample video: {e}")
        self._start_video_stream_source(video_file)

    def _load_custom_video(self):
        """Allows user to select any .mp4 or .avi bus video from disk."""
        file_path = filedialog.askopenfilename(
            title="Select Bus Video for YOLOv11 + ANPR Stream",
            filetypes=[("Video Files", "*.mp4;*.avi;*.mkv;*.mov;*.wmv")]
        )
        if file_path:
            self._start_video_stream_source(file_path)

    def _start_webcam_stream(self):
        """Streams from physical USB webcam or integrated camera."""
        self._start_video_stream_source(0)

    def _start_video_stream_source(self, source):
        # Stop photo auto-stream if active
        if self.is_auto_streaming:
            self._toggle_auto_stream()

        self.active_video_source = source
        started = self.video_engine.start_stream(source)
        if started:
            self.is_video_streaming = True
            source_lbl = os.path.basename(str(source)) if isinstance(source, str) else f"Webcam {source}"
            self.live_badge_text.configure(text=f"● STREAMING: {source_lbl}")
            self.live_indicator.configure(fg_color="#16a34a")
            if hasattr(self, "pause_resume_btn"):
                self.pause_resume_btn.configure(text="⏸ Pause", fg_color="#b45309", state="normal")
            
            # Start UI video render tick
            self._video_tick()

    def _pause_video_stream(self):
        if not self.is_video_streaming:
            return
        if self.video_engine.is_paused:
            self.video_engine.resume_stream()
            if hasattr(self, "pause_resume_btn"):
                self.pause_resume_btn.configure(text="⏸ Pause", fg_color="#b45309")
            self.live_badge_text.configure(text="● STREAMING ACTIVE")
            self.live_indicator.configure(fg_color="#16a34a")
        else:
            self.video_engine.pause_stream()
            if hasattr(self, "pause_resume_btn"):
                self.pause_resume_btn.configure(text="▶ Resume", fg_color="#16a34a")
            self.live_badge_text.configure(text="⏸ PAUSED")
            self.live_indicator.configure(fg_color="#f59e0b")

    def _stop_video_stream(self):
        self.is_video_streaming = False
        if hasattr(self, "_video_timer") and self._video_timer:
            try:
                self.after_cancel(self._video_timer)
            except Exception:
                pass
            self._video_timer = None

        self.video_engine.stop_stream()
        if hasattr(self, "pause_resume_btn"):
            self.pause_resume_btn.configure(text="⏸ Pause", fg_color="#b45309")
        self.live_badge_text.configure(text="⏹ STREAM STOPPED")
        self.live_indicator.configure(fg_color="#dc2626")
        self._refresh_all_data()

    def _video_tick(self):
        """Smooth 25-30 FPS UI frame display tick."""
        if not self.is_video_streaming or not self.winfo_exists():
            return

        frame = self.video_engine.get_latest_frame()
        if frame is not None:
            try:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb_frame)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(680, 380))
                self._current_video_img = ctk_img
                self.video_label.configure(image=ctk_img, text="")
                
                # Update bottom sensor telemetry
                fps = self.video_engine.current_fps
                lat = self.video_engine.yolo_latency_ms
                self.sensor_telemetry_lbl.configure(text=f"Live Feed: {fps:.1f} FPS • YOLOv11: {lat:.1f}ms • ANPR Active")
            except Exception as e:
                pass

        # Schedule next tick at ~35ms
        if self.is_video_streaming and self.winfo_exists():
            self._video_timer = self.after(35, self._video_tick)

    def _on_video_detection_event(self, data: dict):
        """Thread-safe event callback triggered when a bus is confirmed parked (5s hold)."""
        try:
            if self.winfo_exists():
                self.after(0, lambda: self._apply_video_detection_ui(data))
        except Exception:
            pass

    def _apply_video_detection_ui(self, data: dict):
        """Dynamically synchronizes manifest, detections list, and timeline to the video-detected bus."""
        try:
            if not self.winfo_exists():
                return
            plate = data.get("plate_number")
            bay = data.get("bay_id")
            if plate:
                self.selected_bus = plate
                if plate not in self.current_bus_list:
                    self.current_bus_list.append(plate)
                    self.bus_dropdown.configure(values=self.current_bus_list)
                self.bus_dropdown.set(plate)
                
                # Immediately refresh manifest and timeline with zero lag
                self._load_manifest()
                self._load_detections()
                self._load_timeline()
        except Exception as e:
            print(f"[UI SYNC NOTICE]: {e}")

    def _test_sample_image(self, img_filename, bus_reg):
        """Immediately loads and processes the specified real bus sample photo."""
        if self.is_video_streaming:
            self._stop_video_stream()
            
        self.selected_bus = bus_reg
        self.bus_dropdown.set(bus_reg)
        full_path = os.path.abspath(img_filename)
        self._trigger_ai_detection(custom_path=full_path)

    def _build_content(self):
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=2, column=0, sticky="nsew", padx=32, pady=(0, 16))
        
        content_frame.grid_columnconfigure(0, weight=2)
        content_frame.grid_columnconfigure(1, weight=1)

        # Left Column
        left_col = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        
        # 1. Video Canvas Panel
        video_card = ctk.CTkFrame(left_col, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        video_card.pack(fill="x", pady=(0, 16))
        
        self.video_placeholder = ctk.CTkFrame(video_card, fg_color="#090d16", height=420, corner_radius=8)
        self.video_placeholder.pack(fill="x", padx=4, pady=4)
        self.video_placeholder.pack_propagate(False)

        # Video Canvas Label for Image
        self.video_label = ctk.CTkLabel(self.video_placeholder, text="")
        self.video_label.place(relx=0.5, rely=0.5, anchor="center")

        # Top Overlays
        top_tags = ctk.CTkFrame(self.video_placeholder, fg_color="transparent")
        top_tags.pack(anchor="nw", padx=16, pady=16)
        
        self.live_indicator = ctk.CTkFrame(top_tags, fg_color="#dc2626", corner_radius=12)
        self.live_indicator.pack(side="left", padx=4)
        ctk.CTkLabel(self.live_indicator, text="●", text_color="#fca5a5", font=("Arial", 10)).pack(side="left", padx=(8, 2), pady=2)
        self.live_badge_text = ctk.CTkLabel(self.live_indicator, text="LIVE CCTV", text_color="#ffffff", font=("Inter", 10, "bold"))
        self.live_badge_text.pack(side="left", padx=(0, 8), pady=2)
        
        ctk.CTkLabel(top_tags, text="YOLOv11 Bus Tracker", font=FONTS["data_mono"], text_color="#ffffff", fg_color="#1e293b", corner_radius=4).pack(side="left", padx=4, ipadx=8, ipady=4)
        ctk.CTkLabel(top_tags, text="EasyOCR ANPR", font=FONTS["data_mono"], text_color="#38bdf8", fg_color="#0f172a", corner_radius=4).pack(side="left", padx=4, ipadx=8, ipady=4)

        # Video Bottom Bar
        v_bottom = ctk.CTkFrame(video_card, fg_color="transparent", height=44)
        v_bottom.pack(fill="x", padx=16, pady=8)
        
        ctk.CTkLabel(v_bottom, text="✔", text_color="#10b981", font=("Arial", 14)).pack(side="left")
        ctk.CTkLabel(v_bottom, text="Point-in-Polygon Bay Mapping Active", text_color=COLORS["on_surface_variant"], font=FONTS["label_md"]).pack(side="left", padx=(4, 16))
        
        ctk.CTkLabel(v_bottom, text="⚡", text_color=COLORS["primary"], font=("Arial", 14)).pack(side="left")
        ctk.CTkLabel(v_bottom, text="PostgreSQL Live Sync", text_color=COLORS["on_surface_variant"], font=FONTS["label_md"]).pack(side="left", padx=4)
        
        self.sensor_telemetry_lbl = ctk.CTkLabel(v_bottom, text="Camera Sensor: Sony STARVIS 1080p • 30 FPS", text_color=COLORS["on_surface_variant"], font=FONTS["data_mono"])
        self.sensor_telemetry_lbl.pack(side="right")

        # 2. Live Detected Bus Manifest Card
        self.manifest_card = ctk.CTkFrame(left_col, fg_color=COLORS["surface_container_lowest"], border_color="#0284c7", border_width=2, corner_radius=12)
        self.manifest_card.pack(fill="x", pady=(0, 16))
        
        m_head = ctk.CTkFrame(self.manifest_card, fg_color="#f0f9ff", corner_radius=10)
        m_head.pack(fill="x", padx=2, pady=(2, 0))
        m_head_content = ctk.CTkFrame(m_head, fg_color="transparent")
        m_head_content.pack(fill="x", padx=16, pady=10)

        left_m = ctk.CTkFrame(m_head_content, fg_color="transparent")
        left_m.pack(side="left")
        ctk.CTkLabel(left_m, text="LIVE DETECTED VEHICLE MANIFEST & TELEMETRY", font=("Inter", 12, "bold"), text_color="#0284c7").pack(anchor="w")
        ctk.CTkLabel(left_m, text="Automatically resolved from PostgreSQL using recognized plate & spatial bay mapping", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")

        right_m = ctk.CTkFrame(m_head_content, fg_color="transparent")
        right_m.pack(side="right")

        self.manifest_status_badge = ctk.CTkLabel(right_m, text="BOARDING", font=("Inter", 11, "bold"), fg_color="#dcfce7", text_color="#15803d", corner_radius=6)
        self.manifest_status_badge.pack(side="left", padx=4, ipadx=8, ipady=4)

        # Manifest Container for details grid
        self.manifest_container = ctk.CTkFrame(self.manifest_card, fg_color="transparent")
        self.manifest_container.pack(fill="x", padx=16, pady=16)

        # Manifest Bottom Navigation Actions
        m_actions = ctk.CTkFrame(self.manifest_card, fg_color="#f8fafc", corner_radius=10)
        m_actions.pack(fill="x", padx=2, pady=(0, 2))
        m_act_content = ctk.CTkFrame(m_actions, fg_color="transparent")
        m_act_content.pack(fill="x", padx=16, pady=8)

        ctk.CTkLabel(m_act_content, text="Quick Actions for Detected Bus:", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(side="left")

        ctk.CTkButton(
            m_act_content, text="🅿 Inspect Bay in Manager", font=FONTS["label_md"], height=28,
            fg_color="transparent", text_color=COLORS["primary"], border_color=COLORS["outline_variant"], border_width=1,
            hover_color=COLORS["surface_variant"],
            command=lambda: self.app_controller.show_view("ParkingBayManagement") if self.app_controller else None
        ).pack(side="right", padx=4)

        ctk.CTkButton(
            m_act_content, text="⏱ View Full Schedule", font=FONTS["label_md"], height=28,
            fg_color="transparent", text_color=COLORS["primary"], border_color=COLORS["outline_variant"], border_width=1,
            hover_color=COLORS["surface_variant"],
            command=lambda: self.app_controller.show_view("ScheduleAndTimings") if self.app_controller else None
        ).pack(side="right", padx=4)

        ctk.CTkButton(
            m_act_content, text="📑 Open ANPR Logs", font=FONTS["label_md"], height=28,
            fg_color="transparent", text_color=COLORS["primary"], border_color=COLORS["outline_variant"], border_width=1,
            hover_color=COLORS["surface_variant"],
            command=lambda: self.app_controller.show_view("ANPRRecords") if self.app_controller else None
        ).pack(side="right", padx=4)

        # Right Column
        right_col = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew")

        # 1. Camera Info
        info_card = ctk.CTkFrame(right_col, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        info_card.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(info_card, text="Camera & Sensor Telemetry", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(anchor="w", padx=16, pady=(16, 8))
        
        info_grid = ctk.CTkFrame(info_card, fg_color="transparent")
        info_grid.pack(fill="x", padx=16, pady=8)
        info_grid.grid_columnconfigure(0, weight=1)
        info_grid.grid_columnconfigure(1, weight=1)

        infos = [
            ("Camera ID", "CAM-01"), ("Location", "Terminal Bay Area"), 
            ("Stream Status", "LIVE 🟢"), ("Network", "Gigabit PoE"),
            ("Resolution", "1280 x 720 @ 30fps"), ("Inference Latency", "32 ms"),
            ("Detector", "YOLOv11n (COCO)"), ("ANPR Engine", "EasyOCR (CRAFT+CRNN)")
        ]

        for i, (k, v) in enumerate(infos):
            cell = ctk.CTkFrame(info_grid, fg_color="transparent")
            cell.grid(row=i//2, column=i%2, sticky="w", pady=4)
            ctk.CTkLabel(cell, text=k, font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
            ctk.CTkLabel(cell, text=v, font=FONTS["body_md"], text_color=COLORS["on_surface"]).pack(anchor="w")

        # 2. AI Detections Card
        ai_card = ctk.CTkFrame(right_col, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        ai_card.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(ai_card, text="Recent AI Vision Detections", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(anchor="w", padx=16, pady=(16, 8))

        self.ai_card_container = ctk.CTkFrame(ai_card, fg_color="transparent")
        self.ai_card_container.pack(fill="x", padx=16, pady=8)

        # 3. AI Detection Timeline Card
        timeline_card = ctk.CTkFrame(right_col, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        timeline_card.pack(fill="x")
        
        ctk.CTkLabel(timeline_card, text="AI Event Sequence Timeline", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(anchor="w", padx=16, pady=(16, 8))
        
        self.timeline_list_container = ctk.CTkFrame(timeline_card, fg_color="transparent")
        self.timeline_list_container.pack(fill="x", padx=16, pady=8)

    def _on_bus_select(self, choice):
        self.selected_bus = choice
        self._trigger_ai_detection()

    def _load_custom_image(self):
        """Allows user to browse and upload ANY real bus image file on their machine."""
        if self.is_video_streaming:
            self._stop_video_stream()

        file_path = filedialog.askopenfilename(
            title="Select Real Bus Image for YOLOv11 + ANPR",
            filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")]
        )
        if file_path:
            self._trigger_ai_detection(custom_path=file_path)

    def _toggle_auto_stream(self):
        """Starts or stops continuous real-time cycling between both sample buses."""
        if self.is_video_streaming:
            self._stop_video_stream()

        if self.is_auto_streaming:
            self.is_auto_streaming = False
            self.cycle_btn.configure(text="🔄 Auto-Cycle Photos", fg_color="transparent")
            self.live_badge_text.configure(text="LIVE CCTV")
            self.live_indicator.configure(fg_color="#dc2626")
            if self._stream_timer:
                self.after_cancel(self._stream_timer)
                self._stream_timer = None
        else:
            self.is_auto_streaming = True
            self.cycle_btn.configure(text="⏹ Stop Auto-Cycle", fg_color="#fee2e2")
            self.live_badge_text.configure(text="PHOTO STREAM ACTIVE")
            self.live_indicator.configure(fg_color="#16a34a")
            self._stream_step()

    def _stream_step(self):
        if not self.is_auto_streaming or not self.winfo_exists():
            return
        samples = [
            ("sample_bus_1_TN01AN2345.jpg", "TN 01 AN 2345"),
            ("sample_bus_2_TN38N4567.jpg", "TN 38 N 4567")
        ]
        sample_img, bus_reg = samples[self._sample_cycle_idx % len(samples)]
        self._sample_cycle_idx += 1
        self.selected_bus = bus_reg
        self.bus_dropdown.set(bus_reg)
        self._trigger_ai_detection(custom_path=os.path.abspath(sample_img))
        self._stream_timer = self.after(5000, self._stream_step)

    def _refresh_all_data(self):
        """Loads video frame, manifest, detections, and timeline."""
        if not self.is_video_streaming:
            self._load_video_preview()
        self._load_manifest()
        self._load_detections()
        self._load_timeline()

    def _load_video_preview(self):
        """Displays annotated CCTV frame in video container."""
        img_candidates = ["live_cctv_annotated.jpg", "test_detection_output.jpg", "real_bus_sample.jpg"]
        image_path = None
        for cand in img_candidates:
            if os.path.exists(cand):
                image_path = cand
                break

        if image_path:
            try:
                pil_img = Image.open(image_path)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(680, 380))
                self.video_label.configure(image=ctk_img, text="")
            except Exception as e:
                self.video_label.configure(text=f"Image preview notice: {e}", image=None)
        else:
            self.video_label.configure(text="No active CCTV frame found.\nClick 'Play Terminal Video' above.", font=FONTS["body_md"], text_color="#94a3b8")

    def _load_manifest(self):
        """Queries and renders user-friendly manifest details for the detected bus."""
        for child in self.manifest_container.winfo_children():
            child.destroy()

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT b.registration_no, b.bus_type, b.capacity, b.status, b.driver_name,
                       s.route, s.destination, s.bay, s.departure_time, s.fare, s.status,
                       r.via_stops, r.distance_km
                FROM buses b
                LEFT JOIN schedules s ON s.bus_no = b.registration_no
                LEFT JOIN routes r ON r.source || ' - ' || r.destination LIKE '%' || s.destination || '%' OR r.route_id = 'R-01'
                WHERE b.registration_no = %s
            """, (self.selected_bus,))
            row = cur.fetchone()
            
            # Fetch latest confidence from detections
            cur.execute("""
                SELECT confidence, bay_id FROM detections 
                WHERE bus_registration = %s 
                ORDER BY timestamp DESC LIMIT 1
            """, (self.selected_bus,))
            det_row = cur.fetchone()
            conn.close()

            if not row:
                ctk.CTkLabel(self.manifest_container, text=f"No manifest registered for vehicle {self.selected_bus}", font=FONTS["body_md"]).pack()
                return

            reg, b_type, cap, b_status, driver, route, dest, bay, dep, fare, s_status, via, dist = row
            det_conf = round(float(det_row[0]), 1) if det_row else 94.2
            det_bay = det_row[1] if det_row else (bay if bay else "B02")

            status_text = s_status if s_status else "BOARDING"
            self.manifest_status_badge.configure(text=f"● {status_text}")

            # 4 Columns Grid (2 rows x 4 cols = 8 cards)
            grid = ctk.CTkFrame(self.manifest_container, fg_color="transparent")
            grid.pack(fill="x")
            for col_idx in range(4):
                grid.grid_columnconfigure(col_idx, weight=1, uniform="m_col")

            fields = [
                ("REGISTRATION NUMBER", reg, "#0284c7", True),
                ("ASSIGNED PARKING BAY", f"Bay {det_bay} (Ground Docked)", "#16a34a", False),
                ("ROUTE & DESTINATION", f"{dest if dest else 'Central Hub'}", "#0f172a", False),
                ("SCHEDULED DEPARTURE", f"⏱ {dep if dep else '12:00 PM'}", "#b45309", False),
                
                ("BUS MODEL / CLASS", f"{b_type} ({cap} Seats)", "#334155", False),
                ("ASSIGNED DRIVER", f"👨‍✈ {driver if driver else 'Fleet Operator'}", "#334155", False),
                ("SERVICE & VIA STOPS", f"{route if route else 'Express'}", "#334155", False),
                ("STANDARD FARE / RATE", f"{fare if fare else 'Rs 500.00'}", "#059669", False),
            ]

            for idx, (title, val, color, is_badge) in enumerate(fields):
                r = idx // 4
                c = idx % 4
                cell = ctk.CTkFrame(grid, fg_color=COLORS["surface_container_low"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=8)
                cell.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)

                cell_inner = ctk.CTkFrame(cell, fg_color="transparent")
                cell_inner.pack(fill="both", expand=True, padx=12, pady=10)

                ctk.CTkLabel(cell_inner, text=title, font=("Inter", 9, "bold"), text_color=COLORS["on_surface_variant"]).pack(anchor="w")
                
                if is_badge:
                    b_frame = ctk.CTkFrame(cell_inner, fg_color="#e0f2fe", corner_radius=4)
                    b_frame.pack(anchor="w", pady=(4, 0))
                    ctk.CTkLabel(b_frame, text=val, font=("Inter", 13, "bold"), text_color=color).pack(padx=8, pady=2)
                else:
                    ctk.CTkLabel(cell_inner, text=val, font=("Inter", 11, "bold"), text_color=color, wraplength=140, justify="left").pack(anchor="w", pady=(4, 0))

        except Exception as e:
            ctk.CTkLabel(self.manifest_container, text=f"Manifest load notice: {e}", font=FONTS["label_md"], text_color=COLORS["error"]).pack()

    def _load_detections(self):
        """Populate recent detections from PostgreSQL."""
        for child in self.ai_card_container.winfo_children():
            child.destroy()

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT bus_registration, bay_id, confidence, timestamp FROM detections ORDER BY timestamp DESC LIMIT 3")
            rows = cur.fetchall()
            conn.close()

            if not rows:
                ctk.CTkLabel(self.ai_card_container, text="No detections recorded yet.", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(pady=8)
                return

            for i, (reg, bay, conf, ts) in enumerate(rows):
                time_str = ts.strftime("%H:%M:%S") if hasattr(ts, "strftime") else str(ts)[11:19]
                bg_col = "#f0f9ff" if i == 0 else COLORS["surface_container_lowest"]
                border_col = "#0284c7" if i == 0 else COLORS["outline_variant"]

                card = ctk.CTkFrame(self.ai_card_container, fg_color=bg_col, border_color=border_col, border_width=1, corner_radius=8)
                card.pack(fill="x", pady=4)

                top_r = ctk.CTkFrame(card, fg_color="transparent")
                top_r.pack(fill="x", padx=10, pady=(8, 2))
                ctk.CTkLabel(top_r, text=f"Bus • {int(conf)}% Conf.", font=FONTS["label_md"], text_color=COLORS["primary"]).pack(side="left")
                ctk.CTkLabel(top_r, text=time_str, font=FONTS["data_mono"], text_color=COLORS["on_surface_variant"]).pack(side="right")

                ctk.CTkLabel(card, text=reg, font=("Inter", 13, "bold"), text_color=COLORS["on_surface"]).pack(anchor="w", padx=10)
                
                bot_r = ctk.CTkFrame(card, fg_color="transparent")
                bot_r.pack(fill="x", padx=10, pady=(2, 8))
                badge = ctk.CTkFrame(bot_r, fg_color="#dbeafe", corner_radius=4)
                badge.pack(side="left")
                ctk.CTkLabel(badge, text=f"Bay: {bay}", font=FONTS["label_md"], text_color="#1d4ed8").pack(padx=6, pady=2)

                verified_lbl = ctk.CTkLabel(bot_r, text="✔ Verified Match", font=("Inter", 11), text_color="#16a34a")
                verified_lbl.pack(side="right")
        except Exception as e:
            ctk.CTkLabel(self.ai_card_container, text=f"DB Error: {e}", font=FONTS["label_md"], text_color=COLORS["error"]).pack()

    def _load_timeline(self):
        """Populate detection timeline with step-by-step milestones."""
        for child in self.timeline_list_container.winfo_children():
            child.destroy()

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT timestamp, title, description FROM events ORDER BY timestamp DESC LIMIT 4")
            events = cur.fetchall()
            conn.close()

            if not events:
                ctk.CTkLabel(self.timeline_list_container, text="No events logged.", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(pady=8)
                return

            for i, row in enumerate(events):
                raw_time = str(row[0])
                time_part = raw_time.split(" ")[1] if " " in raw_time else raw_time
                time_str = time_part.split(".")[0]
                title = str(row[1]).encode('ascii', 'replace').decode('ascii')
                desc = str(row[2]).encode('ascii', 'replace').decode('ascii') if row[2] else ""

                item = ctk.CTkFrame(self.timeline_list_container, fg_color="transparent")
                item.pack(fill="x", pady=4)

                # Dot
                dot = ctk.CTkFrame(item, fg_color="#0284c7" if i == 0 else COLORS["outline_variant"], width=8, height=8, corner_radius=4)
                dot.pack(side="left", padx=(0, 8), pady=4)

                # Text Column
                col = ctk.CTkFrame(item, fg_color="transparent")
                col.pack(side="left", fill="x", expand=True)

                row1 = ctk.CTkFrame(col, fg_color="transparent")
                row1.pack(fill="x")
                ctk.CTkLabel(row1, text=title, font=("Inter", 11, "bold"), text_color=COLORS["on_surface"]).pack(side="left")
                ctk.CTkLabel(row1, text=time_str, font=FONTS["data_mono"], text_color=COLORS["on_surface_variant"]).pack(side="right")

                if desc:
                    ctk.CTkLabel(col, text=desc, font=("Inter", 10), text_color=COLORS["on_surface_variant"], justify="left").pack(anchor="w")
        except Exception as e:
            ctk.CTkLabel(self.timeline_list_container, text=f"Timeline Error: {e}", font=FONTS["label_md"], text_color=COLORS["error"]).pack()

    def _trigger_ai_detection(self, custom_path=None):
        """Runs live detection on the selected bus or image path in a background thread."""
        if self.is_detecting:
            return
        self.is_detecting = True
        self.detect_btn.configure(text="⏳ Running AI...", state="disabled")

        bus_target = custom_path if custom_path else self.selected_bus

        def run_bg():
            try:
                import subprocess
                subprocess.run([sys.executable, "generate_detection.py", bus_target], check=True)
            except Exception as e:
                print(f"AI Detection error: {e}")
            finally:
                self.after(300, self._on_detection_complete)

        threading.Thread(target=run_bg, daemon=True).start()

    def _on_detection_complete(self):
        self.is_detecting = False
        self.detect_btn.configure(text="⚡ Run Photo AI", state="normal")
        
        # Sync selected_bus with latest detected vehicle in DB
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT bus_registration FROM detections ORDER BY timestamp DESC LIMIT 1")
            row = cur.fetchone()
            if row:
                self.selected_bus = row[0]
                if self.selected_bus in self.current_bus_list:
                    self.bus_dropdown.set(self.selected_bus)
            conn.close()
        except Exception:
            pass

        self._refresh_all_data()

    def destroy(self):
        if hasattr(self, "video_engine") and self.video_engine:
            self.video_engine.stop_stream()
        if hasattr(self, "_video_timer") and self._video_timer:
            try:
                self.after_cancel(self._video_timer)
            except Exception:
                pass
        if hasattr(self, "_stream_timer") and self._stream_timer:
            try:
                self.after_cancel(self._stream_timer)
            except Exception:
                pass
        super().destroy()
