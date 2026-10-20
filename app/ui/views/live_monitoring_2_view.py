import customtkinter as ctk
from app.constants import COLORS, FONTS

class LiveMonitoring2View(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.app_controller = app_controller
        
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_content()

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
            left, text="Camera Detail: CAM-01 (Main Entrance)", font=FONTS["headline_lg"], text_color=COLORS["on_surface"]
        ).pack(anchor="w")

        right = ctk.CTkFrame(header_frame, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")
        
        ctk.CTkButton(
            right, text="📷 Snapshot", fg_color=COLORS["surface_container_high"], text_color=COLORS["primary"],
            border_color=COLORS["primary_fixed_dim"], border_width=1, hover_color=COLORS["surface_container_highest"]
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            right, text="⚙ Configure AI", fg_color=COLORS["primary"], text_color=COLORS["on_primary"], hover_color=COLORS["primary_container"]
        ).pack(side="left", padx=4)

    def _build_content(self):
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=32, pady=16)
        
        content_frame.grid_columnconfigure(0, weight=2)
        content_frame.grid_columnconfigure(1, weight=1)

        # Left Column
        left_col = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        
        # 1. Big Video Panel
        video_card = ctk.CTkFrame(left_col, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        video_card.pack(fill="x", pady=(0, 16))
        
        video_placeholder = ctk.CTkFrame(video_card, fg_color="#1c1c1c", height=400, corner_radius=0)
        video_placeholder.pack(fill="x", padx=1, pady=1)
        video_placeholder.pack_propagate(False)

        # Overlays on video
        top_tags = ctk.CTkFrame(video_placeholder, fg_color="transparent")
        top_tags.pack(anchor="nw", padx=16, pady=16)
        
        live_tag = ctk.CTkFrame(top_tags, fg_color="#b91c1c", corner_radius=12)
        live_tag.pack(side="left", padx=4)
        ctk.CTkLabel(live_tag, text="●", text_color="#fca5a5", font=("Arial", 10)).pack(side="left", padx=(8,2), pady=2)
        ctk.CTkLabel(live_tag, text="LIVE", text_color="#ffffff", font=("Inter", 10, "bold")).pack(side="left", padx=(0,8), pady=2)
        
        ctk.CTkLabel(top_tags, text="YOLOv11 Active", font=FONTS["data_mono"], text_color="#ffffff", fg_color="#334155", corner_radius=4).pack(side="left", padx=4, ipadx=8, ipady=4)

        # Bottom Bar
        v_bottom = ctk.CTkFrame(video_card, fg_color="transparent", height=48)
        v_bottom.pack(fill="x", padx=16, pady=12)
        
        ctk.CTkLabel(v_bottom, text="✔", text_color="#10b981", font=("Arial", 14)).pack(side="left")
        ctk.CTkLabel(v_bottom, text="Tracking Active", text_color=COLORS["on_surface_variant"], font=FONTS["label_md"]).pack(side="left", padx=(4, 16))
        
        ctk.CTkLabel(v_bottom, text="👁", text_color=COLORS["primary"], font=("Arial", 16)).pack(side="left")
        ctk.CTkLabel(v_bottom, text="ANPR Enabled", text_color=COLORS["on_surface_variant"], font=FONTS["label_md"]).pack(side="left", padx=4)
        
        ctk.CTkLabel(v_bottom, text="Uptime: 99.9%", text_color=COLORS["on_surface_variant"], font=FONTS["data_mono"]).pack(side="right")

        # 2. Timeline
        timeline_card = ctk.CTkFrame(left_col, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        timeline_card.pack(fill="x")
        
        ctk.CTkLabel(timeline_card, text="AI Detection Timeline", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(anchor="w", padx=16, pady=(16, 8))
        
        timeline_list = ctk.CTkFrame(timeline_card, fg_color="transparent")
        timeline_list.pack(fill="x", padx=16, pady=8)

        events = [
            ("10:32:09", "Record matched", "Vehicle verified against manifest."),
            ("10:32:08", "Bay 12 identified", ""),
            ("10:32:07", "Plate recognized", "TN 01 AN 2345"),
            ("10:32:06", "Tracking confirmed", ""),
            ("10:32:05", "Bus detected", "")
        ]

        for i, (time, title, desc) in enumerate(events):
            item = ctk.CTkFrame(timeline_list, fg_color="transparent")
            item.pack(fill="x", pady=0)
            
            # Left timeline graphic
            timeline_gfx = ctk.CTkFrame(item, fg_color="transparent", width=24)
            timeline_gfx.pack(side="left", fill="y", padx=(0, 16))
            timeline_gfx.pack_propagate(False)
            
            # Top line
            if i > 0:
                top_line = ctk.CTkFrame(timeline_gfx, fg_color=COLORS["surface_container_high"], width=2, height=14)
                top_line.place(relx=0.5, y=0, anchor="n")
            
            # Bottom line
            if i < len(events) - 1:
                bottom_line = ctk.CTkFrame(timeline_gfx, fg_color=COLORS["surface_container_high"], width=2)
                bottom_line.place(relx=0.5, y=14, relheight=1.0, anchor="n")
            
            # Dot
            if i == 0:
                dot = ctk.CTkFrame(timeline_gfx, fg_color=COLORS["surface"], border_color=COLORS["primary"], border_width=3, width=14, height=14, corner_radius=7)
            else:
                dot = ctk.CTkFrame(timeline_gfx, fg_color=COLORS["surface_container_high"], width=10, height=10, corner_radius=5)
            dot.place(relx=0.5, y=14, anchor="center")
            
            # Content Row
            content_row = ctk.CTkFrame(item, fg_color="transparent")
            content_row.pack(side="left", fill="x", expand=True, pady=4)
            
            ctk.CTkLabel(content_row, text=time, font=FONTS["data_mono"], text_color=COLORS["outline_variant"], width=60, anchor="w").pack(side="left", anchor="n")
            
            text_col = ctk.CTkFrame(content_row, fg_color="transparent")
            text_col.pack(side="left", fill="x", expand=True, padx=16)
            
            title_row = ctk.CTkFrame(text_col, fg_color="transparent")
            title_row.pack(fill="x", anchor="w")
            ctk.CTkLabel(title_row, text=title, font=FONTS["body_md"], text_color=COLORS["on_surface"]).pack(side="left", anchor="w")
            
            if title == "Plate recognized" and desc:
                badge = ctk.CTkLabel(title_row, text=desc, font=("Inter", 11), text_color=COLORS["primary"], fg_color=COLORS["surface_container"], corner_radius=4)
                badge.pack(side="left", padx=8)
            elif desc:
                ctk.CTkLabel(text_col, text=desc, font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")


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
            ("ID", "CAM-01"), ("Location", "Main Entrance"), 
            ("Status", "LIVE"), ("Network", "Wired (PoE)"),
            ("FPS", "28"), ("Latency", "42ms")
        ]

        for i, (k, v) in enumerate(infos):
            cell = ctk.CTkFrame(info_grid, fg_color="transparent")
            cell.grid(row=i//2, column=i%2, sticky="w", pady=4)
            ctk.CTkLabel(cell, text=k, font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
            ctk.CTkLabel(cell, text=v, font=FONTS["body_md"], text_color=COLORS["on_surface"]).pack(anchor="w")

        # 2. AI Detections
        ai_card = ctk.CTkFrame(right_col, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        ai_card.pack(fill="x")
        
        ctk.CTkLabel(ai_card, text="Current AI Detections", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(anchor="w", padx=16, pady=(16, 8))

        d1 = ctk.CTkFrame(ai_card, fg_color=COLORS["surface_container_low"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=8)
        d1.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(d1, text="Bus • 96% Conf.", font=FONTS["label_md"], text_color=COLORS["primary"]).pack(anchor="w", padx=8, pady=(8,0))
        ctk.CTkLabel(d1, text="TN 01 AN 2345", font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(anchor="w", padx=8)
        ctk.CTkLabel(d1, text="Assigned: Bay 12", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", padx=8, pady=(0,8))

        d2 = ctk.CTkFrame(ai_card, fg_color="transparent", border_color=COLORS["outline_variant"], border_width=1, corner_radius=8)
        d2.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(d2, text="Person • 82% Conf.", font=FONTS["label_md"], text_color=COLORS["tertiary"]).pack(anchor="w", padx=8, pady=(8,0))
        ctk.CTkLabel(d2, text="Pedestrian Zone A", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", padx=8, pady=(0,8))
