import os
import random
import threading
import customtkinter as ctk
from PIL import Image
from app.constants import COLORS, FONTS
from app.db.database import get_connection

class LiveMonitoring2View(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.app_controller = app_controller
        
        self.grid_columnconfigure(0, weight=1)

        self.video_label = None
        self.ai_card_container = None
        self.timeline_list_container = None
        self.is_detecting = False

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
            left, text="Camera Detail: CAM-01 (Bay Terminal & CCTV)", font=FONTS["headline_lg"], text_color=COLORS["on_surface"]
        ).pack(anchor="w")

        right = ctk.CTkFrame(header_frame, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")
        
        self.refresh_btn = ctk.CTkButton(
            right, text="🔄 Refresh", font=FONTS["label_md"],
            fg_color=COLORS["surface_container_high"], text_color=COLORS["primary"],
            border_color=COLORS["outline_variant"], border_width=1, hover_color=COLORS["surface_container_highest"],
            command=self._refresh_all_data
        )
        self.refresh_btn.pack(side="left", padx=4)

        self.detect_btn = ctk.CTkButton(
            right, text="⚡ Run AI Detection", font=FONTS["label_md"],
            fg_color=COLORS["primary"], text_color=COLORS["on_primary"], hover_color=COLORS["primary_container"],
            command=self._trigger_ai_detection
        )
        self.detect_btn.pack(side="left", padx=4)

    def _build_content(self):
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=32, pady=16)
        
        content_frame.grid_columnconfigure(0, weight=2)
        content_frame.grid_columnconfigure(1, weight=1)

        # Left Column
        left_col = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        
        # 1. Video Panel
        video_card = ctk.CTkFrame(left_col, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        video_card.pack(fill="x", pady=(0, 16))
        
        self.video_placeholder = ctk.CTkFrame(video_card, fg_color="#111827", height=420, corner_radius=8)
        self.video_placeholder.pack(fill="x", padx=4, pady=4)
        self.video_placeholder.pack_propagate(False)

        # Video Canvas Label for Image
        self.video_label = ctk.CTkLabel(self.video_placeholder, text="")
        self.video_label.place(relx=0.5, rely=0.5, anchor="center")

        # Overlays on video
        top_tags = ctk.CTkFrame(self.video_placeholder, fg_color="transparent")
        top_tags.pack(anchor="nw", padx=16, pady=16)
        
        live_tag = ctk.CTkFrame(top_tags, fg_color="#dc2626", corner_radius=12)
        live_tag.pack(side="left", padx=4)
        ctk.CTkLabel(live_tag, text="●", text_color="#fca5a5", font=("Arial", 10)).pack(side="left", padx=(8, 2), pady=2)
        ctk.CTkLabel(live_tag, text="LIVE CCTV", text_color="#ffffff", font=("Inter", 10, "bold")).pack(side="left", padx=(0, 8), pady=2)
        
        ctk.CTkLabel(top_tags, text="YOLOv11 Active", font=FONTS["data_mono"], text_color="#ffffff", fg_color="#1e293b", corner_radius=4).pack(side="left", padx=4, ipadx=8, ipady=4)
        ctk.CTkLabel(top_tags, text="EasyOCR ANPR", font=FONTS["data_mono"], text_color="#38bdf8", fg_color="#0f172a", corner_radius=4).pack(side="left", padx=4, ipadx=8, ipady=4)

        # Bottom Bar
        v_bottom = ctk.CTkFrame(video_card, fg_color="transparent", height=48)
        v_bottom.pack(fill="x", padx=16, pady=12)
        
        ctk.CTkLabel(v_bottom, text="✔", text_color="#10b981", font=("Arial", 14)).pack(side="left")
        ctk.CTkLabel(v_bottom, text="Point-in-Polygon Bay Tracking Active", text_color=COLORS["on_surface_variant"], font=FONTS["label_md"]).pack(side="left", padx=(4, 16))
        
        ctk.CTkLabel(v_bottom, text="👁", text_color=COLORS["primary"], font=("Arial", 16)).pack(side="left")
        ctk.CTkLabel(v_bottom, text="PostgreSQL Sync", text_color=COLORS["on_surface_variant"], font=FONTS["label_md"]).pack(side="left", padx=4)
        
        ctk.CTkLabel(v_bottom, text="Latency: 34ms • 30 FPS", text_color=COLORS["on_surface_variant"], font=FONTS["data_mono"]).pack(side="right")

        # 2. Timeline Card
        timeline_card = ctk.CTkFrame(left_col, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        timeline_card.pack(fill="x")
        
        ctk.CTkLabel(timeline_card, text="AI Detection & Event Timeline", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(anchor="w", padx=16, pady=(16, 8))
        
        self.timeline_list_container = ctk.CTkFrame(timeline_card, fg_color="transparent")
        self.timeline_list_container.pack(fill="x", padx=16, pady=8)

        # Right Column
        right_col = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew")

        # 1. Camera Info
        info_card = ctk.CTkFrame(right_col, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        info_card.pack(fill="x", pady=(0, 16))
        
        ctk.CTkLabel(info_card, text="Camera Information", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(anchor="w", padx=16, pady=(16, 8))
        
        info_grid = ctk.CTkFrame(info_card, fg_color="transparent")
        info_grid.pack(fill="x", padx=16, pady=8)
        info_grid.grid_columnconfigure(0, weight=1)
        info_grid.grid_columnconfigure(1, weight=1)

        infos = [
            ("ID", "CAM-01"), ("Location", "Main Terminal"), 
            ("Status", "LIVE"), ("Network", "Gigabit PoE"),
            ("Resolution", "1280 x 720"), ("AI Model", "YOLOv11n + OCR")
        ]

        for i, (k, v) in enumerate(infos):
            cell = ctk.CTkFrame(info_grid, fg_color="transparent")
            cell.grid(row=i//2, column=i%2, sticky="w", pady=4)
            ctk.CTkLabel(cell, text=k, font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
            ctk.CTkLabel(cell, text=v, font=FONTS["body_md"], text_color=COLORS["on_surface"]).pack(anchor="w")

        # 2. AI Detections Card
        self.ai_card = ctk.CTkFrame(right_col, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        self.ai_card.pack(fill="x")
        
        ctk.CTkLabel(self.ai_card, text="Current AI Detections", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(anchor="w", padx=16, pady=(16, 8))

        self.ai_card_container = ctk.CTkFrame(self.ai_card, fg_color="transparent")
        self.ai_card_container.pack(fill="x", padx=16, pady=8)

    def _refresh_all_data(self):
        """Loads live visual preview and queries PostgreSQL for detections & events."""
        self._load_video_preview()
        self._load_detections()
        self._load_timeline()

    def _load_video_preview(self):
        """Displays annotated CCTV frame in video container."""
        image_path = "test_detection_output.jpg"
        if os.path.exists(image_path):
            try:
                pil_img = Image.open(image_path)
                # Display in 16:9 ratio fitting the container (~680x380)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(680, 380))
                self.video_label.configure(image=ctk_img, text="")
            except Exception as e:
                self.video_label.configure(text=f"Frame load error: {e}", image=None)
        else:
            self.video_label.configure(text="No active CCTV frame recorded.\nClick 'Run AI Detection' above to test.", font=FONTS["body_md"], text_color="#94a3b8")

    def _load_detections(self):
        """Populate right column cards with real detections from database."""
        for child in self.ai_card_container.winfo_children():
            child.destroy()

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT bus_registration, bay_id, confidence, timestamp FROM detections ORDER BY timestamp DESC LIMIT 4")
            rows = cur.fetchall()
            conn.close()

            if not rows:
                ctk.CTkLabel(self.ai_card_container, text="No detections recorded yet.", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(pady=8)
                return

            for i, (reg, bay, conf, ts) in enumerate(rows):
                time_str = ts.strftime("%H:%M:%S") if hasattr(ts, "strftime") else str(ts)[:8]
                bg_col = COLORS["surface_container_low"] if i == 0 else "transparent"
                border_col = COLORS["primary"] if i == 0 else COLORS["outline_variant"]

                card = ctk.CTkFrame(self.ai_card_container, fg_color=bg_col, border_color=border_col, border_width=1, corner_radius=8)
                card.pack(fill="x", pady=4)

                top_r = ctk.CTkFrame(card, fg_color="transparent")
                top_r.pack(fill="x", padx=8, pady=(8, 2))
                ctk.CTkLabel(top_r, text=f"Bus • {int(conf)}% Conf.", font=FONTS["label_md"], text_color=COLORS["primary"]).pack(side="left")
                ctk.CTkLabel(top_r, text=time_str, font=FONTS["data_mono"], text_color=COLORS["on_surface_variant"]).pack(side="right")

                ctk.CTkLabel(card, text=reg, font=("Inter", 14, "bold"), text_color=COLORS["on_surface"]).pack(anchor="w", padx=8)
                
                bot_r = ctk.CTkFrame(card, fg_color="transparent")
                bot_r.pack(fill="x", padx=8, pady=(2, 8))
                badge = ctk.CTkFrame(bot_r, fg_color=COLORS["primary_container"], corner_radius=4)
                badge.pack(side="left")
                ctk.CTkLabel(badge, text=f"Bay: {bay}", font=FONTS["label_md"], text_color=COLORS["primary"]).pack(padx=6, pady=2)
        except Exception as e:
            ctk.CTkLabel(self.ai_card_container, text=f"DB Error: {e}", font=FONTS["label_md"], text_color=COLORS["error"]).pack()

    def _load_timeline(self):
        """Populate detection timeline with real events from database."""
        for child in self.timeline_list_container.winfo_children():
            child.destroy()

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT timestamp, title, description, event_type FROM events ORDER BY timestamp DESC LIMIT 5")
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
                item.pack(fill="x", pady=2)

                # Dot
                dot = ctk.CTkFrame(item, fg_color=COLORS["primary"] if i == 0 else COLORS["outline_variant"], width=10, height=10, corner_radius=5)
                dot.pack(side="left", padx=(0, 12))

                # Time
                ctk.CTkLabel(item, text=time_str, font=FONTS["data_mono"], text_color=COLORS["on_surface_variant"], width=65, anchor="w").pack(side="left")

                # Text
                content = ctk.CTkFrame(item, fg_color="transparent")
                content.pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(content, text=title, font=FONTS["body_md"], text_color=COLORS["on_surface"]).pack(anchor="w")
                if desc:
                    ctk.CTkLabel(content, text=desc, font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
        except Exception as e:
            ctk.CTkLabel(self.timeline_list_container, text=f"Timeline Error: {e}", font=FONTS["label_md"], text_color=COLORS["error"]).pack()

    def _trigger_ai_detection(self):
        """Simulates/runs a live AI detection cycle in a background thread."""
        if self.is_detecting:
            return
        self.is_detecting = True
        self.detect_btn.configure(text="⏳ Processing AI...", state="disabled")

        def run_bg():
            try:
                import sys
                import subprocess
                subprocess.run([sys.executable, "test_pipeline.py"], check=True)
            except Exception as e:
                print(f"AI Detection error: {e}")
            finally:
                self.after(500, self._on_detection_complete)

        threading.Thread(target=run_bg, daemon=True).start()

    def _on_detection_complete(self):
        self.is_detecting = False
        self.detect_btn.configure(text="⚡ Run AI Detection", state="normal")
        self._refresh_all_data()
