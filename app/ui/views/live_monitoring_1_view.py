import os
import customtkinter as ctk
from app.constants import COLORS, FONTS

class CameraCard(ctk.CTkFrame):
    def __init__(self, master, cam_id, location, is_live=True, status="LIVE", **kwargs):
        super().__init__(master, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12, **kwargs)
        
        self.pack_propagate(False)

        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=12, border_color=COLORS["outline_variant"], border_width=0)
        header.pack(fill="x", padx=1, pady=1)
        header_border = ctk.CTkFrame(header, fg_color=COLORS["outline_variant"], height=1)
        header_border.pack(side="bottom", fill="x")

        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="x", padx=16, pady=12)

        left_h = ctk.CTkFrame(header_content, fg_color="transparent")
        left_h.pack(side="left")

        ctk.CTkLabel(left_h, text=cam_id, font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(side="left")
        ctk.CTkLabel(left_h, text=location, font=FONTS["label_md"], text_color=COLORS["on_surface_variant"], fg_color=COLORS["surface_container"], corner_radius=12).pack(side="left", padx=8)

        if is_live:
            badge = ctk.CTkFrame(header_content, fg_color="#f0fdf4", border_color="#bbf7d0", border_width=1, corner_radius=12)
            badge.pack(side="right")
            ctk.CTkLabel(badge, text="●", text_color="#22c55e", font=("Arial", 12)).pack(side="left", padx=(8, 2), pady=2)
            ctk.CTkLabel(badge, text=status, text_color="#15803d", font=("Inter", 10, "bold")).pack(side="left", padx=(0, 8), pady=2)
        else:
            badge = ctk.CTkFrame(header_content, fg_color="#fef2f2", border_color="#fecaca", border_width=1, corner_radius=12)
            badge.pack(side="right")
            ctk.CTkLabel(badge, text="⚠", text_color=COLORS["error"], font=("Arial", 12)).pack(side="left", padx=(8, 2), pady=2)
            ctk.CTkLabel(badge, text=status, text_color=COLORS["error"], font=("Inter", 10, "bold")).pack(side="left", padx=(0, 8), pady=2)

        # Video placeholder
        self.video_frame = ctk.CTkFrame(self, fg_color=COLORS["inverse_surface"], corner_radius=0)
        self.video_frame.pack(fill="both", expand=True, padx=1, pady=0)

        # Show CCTV visual frame if live
        if is_live and os.path.exists("test_detection_output.jpg"):
            try:
                from PIL import Image
                img = Image.open("test_detection_output.jpg")
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(480, 260))
                thumb = ctk.CTkLabel(self.video_frame, text="", image=ctk_img)
                thumb.place(relx=0.5, rely=0.5, anchor="center")
            except Exception:
                pass
        
        # Telemetry inside video frame
        if is_live:
            tele_frame = ctk.CTkFrame(self.video_frame, fg_color="#1c1c1c", corner_radius=4)
            tele_frame.pack(side="bottom", anchor="w", padx=12, pady=12)
            
            ctk.CTkLabel(tele_frame, text="FPS: 28", font=FONTS["data_mono"], text_color="#ffffff").pack(side="left", padx=8, pady=4)
            ctk.CTkLabel(tele_frame, text="LAT: 42ms", font=FONTS["data_mono"], text_color="#ffffff").pack(side="left", padx=(0, 8), pady=4)
        else:
            center_msg = ctk.CTkFrame(self.video_frame, fg_color="transparent")
            center_msg.place(relx=0.5, rely=0.5, anchor="center")
            ctk.CTkLabel(center_msg, text="☁", font=("Arial", 32), text_color=COLORS["outline_variant"]).pack()
            ctk.CTkLabel(center_msg, text="Connection lost to camera stream.", font=FONTS["body_md"], text_color=COLORS["outline_variant"]).pack(pady=4)

        # Footer Actions
        footer = ctk.CTkFrame(self, fg_color=COLORS["surface_container_lowest"], corner_radius=12)
        footer.pack(fill="x", padx=1, pady=1)

        footer_content = ctk.CTkFrame(footer, fg_color="transparent")
        footer_content.pack(fill="x", padx=16, pady=12)

        left_actions = ctk.CTkFrame(footer_content, fg_color="transparent")
        left_actions.pack(side="left")
        ctk.CTkButton(left_actions, text="⛶", width=32, height=32, fg_color=COLORS["surface_variant"], text_color=COLORS["on_surface"], hover_color=COLORS["primary"]).pack(side="left")
        ctk.CTkButton(left_actions, text="📷", width=32, height=32, fg_color=COLORS["surface_variant"], text_color=COLORS["on_surface"], hover_color=COLORS["primary"]).pack(side="left", padx=8)

        right_actions = ctk.CTkFrame(footer_content, fg_color="transparent")
        right_actions.pack(side="right")
        self.details_btn = ctk.CTkButton(right_actions, text="Details", font=FONTS["label_md"], fg_color="transparent", border_color=COLORS["primary"], border_width=1, text_color=COLORS["primary"], hover_color=COLORS["primary_container"])
        self.details_btn.pack(side="left", padx=8)
        ctk.CTkButton(right_actions, text="⚙", width=32, height=32, fg_color="transparent", text_color=COLORS["on_surface_variant"], hover_color=COLORS["surface_variant"]).pack(side="left")


class LiveMonitoring1View(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.app_controller = app_controller
        
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_grid()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 16))
        
        ctk.CTkLabel(
            header_frame, text="Live Monitoring", font=FONTS["headline_lg"], text_color=COLORS["on_background"]
        ).pack(anchor="w")
        ctk.CTkLabel(
            header_frame, text="Real-time CCTV monitoring and AI-based bus detection", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]
        ).pack(anchor="w")

    def _build_grid(self):
        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.grid(row=1, column=0, sticky="nsew", padx=32, pady=16)
        
        grid_frame.grid_columnconfigure(0, weight=1, uniform="col")
        grid_frame.grid_columnconfigure(1, weight=1, uniform="col")

        cameras = [
            {"id": "CAM 01", "loc": "Main Entrance", "live": True, "status": "LIVE"},
            {"id": "CAM 02", "loc": "Bay Area A", "live": True, "status": "LIVE"},
            {"id": "CAM 03", "loc": "Bay Area B", "live": True, "status": "LIVE"},
            {"id": "CAM 04", "loc": "Exit Gate", "live": False, "status": "OFFLINE"},
        ]

        for i, cam in enumerate(cameras):
            row = i // 2
            col = i % 2
            
            card = CameraCard(grid_frame, cam_id=cam["id"], location=cam["loc"], is_live=cam["live"], status=cam["status"], height=400)
            card.grid(row=row, column=col, sticky="nsew", padx=12, pady=12)
            
            card.details_btn.configure(command=lambda c=cam["id"]: self.app_controller.show_view("LiveMonitoring2"))
