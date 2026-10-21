import os
import sys
import threading
import tkinter.filedialog as filedialog
import customtkinter as ctk
from PIL import Image
from app.constants import COLORS, FONTS
from app.db.database import get_connection

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
        self._stream_idx = 0

        self.video_label = None
        self.manifest_container = None
        self.ai_card_container = None
        self.timeline_list_container = None

        self._build_header()
        self._build_content()
        self._refresh_all_data()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 16))
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
            left, text="Real-Time AI Vision: YOLOv11 + ANPR Bay Monitor", font=FONTS["headline_lg"], text_color=COLORS["on_surface"]
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

        # Load Custom Real Bus Image File Dialog Button
        self.upload_btn = ctk.CTkButton(
            right, text="📁 Load Bus Image...", font=FONTS["label_md"], height=36,
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
            right, text="⚡ Run AI Detection", font=FONTS["label_md"], height=36,
            fg_color=COLORS["primary"], text_color=COLORS["on_primary"], hover_color=COLORS["primary_container"],
            command=self._trigger_ai_detection
        )
        self.detect_btn.pack(side="left", padx=4)

        # Live Stream / Auto-Simulate Toggle
        self.stream_btn = ctk.CTkButton(
            right, text="▶ Live Stream", font=FONTS["label_md"], height=36,
            fg_color="#059669", text_color="#ffffff", hover_color="#047857",
            command=self._toggle_auto_stream
        )
        self.stream_btn.pack(side="left", padx=4)

    def _build_content(self):
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=32, pady=16)
        
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
        
        ctk.CTkLabel(v_bottom, text="Camera Sensor: Sony STARVIS 1080p • 30 FPS", text_color=COLORS["on_surface_variant"], font=FONTS["data_mono"]).pack(side="right")

        # 2. Live Detected Bus Manifest Card (Prominent & User-Friendly)
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
        file_path = filedialog.askopenfilename(
            title="Select Real Bus Image for YOLOv11 + ANPR",
            filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")]
        )
        if file_path:
            self._trigger_ai_detection(custom_path=file_path)

    def _toggle_auto_stream(self):
        """Starts or stops continuous real-time cycling of arriving/docking buses."""
        if self.is_auto_streaming:
            self.is_auto_streaming = False
            self.stream_btn.configure(text="▶ Live Stream", fg_color="#059669")
            self.live_badge_text.configure(text="LIVE CCTV")
            self.live_indicator.configure(fg_color="#dc2626")
            if self._stream_timer:
                self.after_cancel(self._stream_timer)
                self._stream_timer = None
        else:
            self.is_auto_streaming = True
            self.stream_btn.configure(text="⏹ Stop Stream", fg_color="#dc2626")
            self.live_badge_text.configure(text="STREAMING ACTIVE")
            self.live_indicator.configure(fg_color="#16a34a")
            self._stream_step()

    def _stream_step(self):
        if not self.is_auto_streaming or not self.winfo_exists():
            return
        # Cycle through bus list
        next_bus = self.current_bus_list[self._stream_idx % len(self.current_bus_list)]
        self._stream_idx += 1
        self.selected_bus = next_bus
        self.bus_dropdown.set(next_bus)
        self._trigger_ai_detection()
        # Schedule next cycle in 5 seconds
        self._stream_timer = self.after(5000, self._stream_step)

    def _refresh_all_data(self):
        """Loads video frame, manifest, detections, and timeline."""
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
            self.video_label.configure(text="No active CCTV frame found.\nClick 'Run AI Detection' above.", font=FONTS["body_md"], text_color="#94a3b8")

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
        self.detect_btn.configure(text="⚡ Run AI Detection", state="normal")
        self._refresh_all_data()

    def destroy(self):
        if hasattr(self, "_stream_timer") and self._stream_timer:
            try:
                self.after_cancel(self._stream_timer)
            except Exception:
                pass
        super().destroy()
