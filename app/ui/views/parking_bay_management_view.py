import customtkinter as ctk
from app.constants import COLORS, FONTS
from app.models.parking_bay_model import ParkingBayModel

class ParkingBayManagementView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.app_controller = app_controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) 

        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.grid(row=0, column=0, sticky="nsew")
        self.scroll_container.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_kpi_cards()
        
        self.content_grid = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.content_grid.grid(row=2, column=0, sticky="nsew", padx=32, pady=16)
        
        # Flex layout: Terminal grid gets more space, side panel fixed-ish (or smaller weight)
        self.content_grid.grid_columnconfigure(0, weight=1)
        
        self._build_terminal_grid(self.content_grid)
        self._build_side_panel(self.content_grid)

    def _build_header(self):
        header = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 16))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left, text="Parking Bay Management", font=FONTS["headline_lg"], text_color=COLORS["on_surface"]).pack(anchor="w")

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(
            right, text="📍 Configure Detection Zone", font=FONTS["label_md"], 
            fg_color=COLORS["primary"], text_color=COLORS["on_primary"], hover_color=COLORS["primary_container"]
        ).pack(side="left")

    def _build_kpi_cards(self):
        kpi_container = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        kpi_container.grid(row=1, column=0, sticky="ew", padx=32)
        
        # 5 columns
        for i in range(5):
            kpi_container.grid_columnconfigure(i, weight=1, uniform="kpi")

        kpis = [
            {"title": "TOTAL BAYS", "val": "24", "icon": "⊞", "color": COLORS["outline"], "bg": COLORS["surface_container_lowest"], "accent": None},
            {"title": "AVAILABLE", "val": "8", "icon": "✓", "color": "#10b981", "bg": COLORS["surface_container_lowest"], "accent": "#10b981"},
            {"title": "OCCUPIED", "val": "12", "icon": "🚌", "color": "#3B82F6", "bg": COLORS["surface_container_lowest"], "accent": "#3B82F6"},
            {"title": "RESERVED/MAINT", "val": "3", "icon": "🔧", "color": "#f59e0b", "bg": COLORS["surface_container_lowest"], "accent": "#f59e0b"},
            {"title": "DISABLED", "val": "1", "icon": "⊘", "color": COLORS["error"], "bg": COLORS["surface_container_lowest"], "accent": COLORS["error"]}
        ]

        for i, kpi in enumerate(kpis):
            card = ctk.CTkFrame(kpi_container, fg_color=kpi["bg"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12, height=96)
            card.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 8, 0 if i == 4 else 8))
            card.pack_propagate(False)

            if kpi["accent"]:
                accent_line = ctk.CTkFrame(card, fg_color=kpi["accent"], width=4)
                accent_line.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=16, pady=16)

            ctk.CTkLabel(inner, text=kpi["title"], font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
            
            bottom_row = ctk.CTkFrame(inner, fg_color="transparent")
            bottom_row.pack(fill="x", side="bottom")
            
            ctk.CTkLabel(bottom_row, text=kpi["val"], font=("Inter", 28, "bold"), text_color=kpi["color"] if kpi["color"] != COLORS["outline"] else COLORS["on_surface"]).pack(side="left")
            ctk.CTkLabel(bottom_row, text=kpi["icon"], font=("Arial", 20), text_color=kpi["color"]).pack(side="right")

    def _build_terminal_grid(self, parent):
        term_card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        term_card.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        
        # Header
        header = ctk.CTkFrame(term_card, fg_color=COLORS["surface_bright"], corner_radius=12)
        header.pack(fill="x", padx=1, pady=1)
        h_inner = ctk.CTkFrame(header, fg_color="transparent")
        h_inner.pack(fill="x", padx=16, pady=12)
        
        ctk.CTkLabel(h_inner, text="Terminal A Layout", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(side="left")
        
        legend = ctk.CTkFrame(h_inner, fg_color="transparent")
        legend.pack(side="right")
        for color, text in [("#10b981", "Available"), ("#3B82F6", "Occupied"), ("#f59e0b", "Maintenance"), (COLORS["error"], "Disabled")]:
            ctk.CTkLabel(legend, text="●", text_color=color, font=("Arial", 12)).pack(side="left", padx=(8, 4))
            ctk.CTkLabel(legend, text=text, font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(side="left")

        # Grid Content
        border = ctk.CTkFrame(term_card, fg_color=COLORS["outline_variant"], height=1)
        border.pack(fill="x", padx=1)
        
        grid_area = ctk.CTkFrame(term_card, fg_color="transparent")
        grid_area.pack(fill="both", expand=True, padx=16, pady=16)
        
        # Configure a 4-column grid for the bays
        for i in range(4):
            grid_area.grid_columnconfigure(i, weight=1, uniform="bay")

        bays = ParkingBayModel.get_all_bays()

        row_idx = 0
        col_idx = 0
        
        for bay in bays:
            # Format status type properly for UI handling
            bay_type = bay["status"].lower()
            
            # Determine styles
            border_color = COLORS["outline_variant"]
            accent_color = None
            if bay_type == "occupied":
                border_color = "#3B82F6"
            elif bay_type == "available":
                accent_color = "#10b981"
            elif bay_type == "maintenance":
                accent_color = "#f59e0b"
            elif bay_type == "disabled":
                accent_color = COLORS["error"]

            bay_frame = ctk.CTkFrame(grid_area, fg_color=COLORS["surface_container_lowest"], border_color=border_color, border_width=1, corner_radius=8, height=130)
            bay_frame.grid(row=row_idx, column=col_idx, sticky="nsew", padx=8, pady=8)
            bay_frame.pack_propagate(False)

            if accent_color:
                # Top accent line
                ctk.CTkFrame(bay_frame, fg_color=accent_color, height=4, corner_radius=0).pack(fill="x")
                
            inner = ctk.CTkFrame(bay_frame, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=12, pady=8)
            
            # Bay ID Header
            header = ctk.CTkFrame(inner, fg_color="transparent")
            header.pack(fill="x", pady=(0, 4))
            ctk.CTkLabel(header, text=bay["bay_id"], font=("Inter", 16, "bold"), text_color=COLORS["on_surface"]).pack(side="left")
            
            # Action dot menu
            ctk.CTkButton(header, text="⋮", width=20, height=20, fg_color="transparent", text_color=COLORS["on_surface_variant"], hover_color=COLORS["surface_container"]).pack(side="right")

            # Content based on state
            if bay_type == "occupied":
                ctk.CTkLabel(inner, text="🚌 " + str(bay["vehicle_reg"]), font=("Inter", 14, "bold"), text_color="#3B82F6").pack(anchor="w", pady=(8, 2))
                ctk.CTkLabel(inner, text="System Detected", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
            elif bay_type == "available":
                empty_state = ctk.CTkFrame(inner, fg_color="transparent")
                empty_state.pack(fill="both", expand=True)
                ctk.CTkLabel(empty_state, text="Available for\nallocation", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"], justify="left").pack(anchor="w", pady=12)
            else:
                # maintenance or disabled
                empty_state = ctk.CTkFrame(inner, fg_color="transparent")
                empty_state.pack(fill="both", expand=True)
                ctk.CTkLabel(empty_state, text=bay["status"].upper(), font=FONTS["label_md"], text_color=accent_color).pack(anchor="w", pady=(8, 2))

            col_idx += 1
            if col_idx >= 4:
                col_idx = 0
                row_idx += 1

    def _build_side_panel(self, parent):
        side_panel = ctk.CTkFrame(parent, fg_color="transparent", width=360)
        side_panel.grid(row=0, column=1, sticky="nsew")
        
        # Details Panel
        details = ctk.CTkFrame(side_panel, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        details.pack(fill="x", pady=(0, 24))
        
        d_head = ctk.CTkFrame(details, fg_color=COLORS["surface_container"], corner_radius=12)
        d_head.pack(fill="x", padx=1, pady=1)
        d_h_inner = ctk.CTkFrame(d_head, fg_color="transparent")
        d_h_inner.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(d_h_inner, text="Bay Details: A01", font=("Inter", 16, "bold"), text_color=COLORS["on_surface"]).pack(side="left")
        
        badge_occ = ctk.CTkFrame(d_h_inner, fg_color="#dbeafe", corner_radius=4)
        badge_occ.pack(side="right")
        ctk.CTkLabel(badge_occ, text="OCCUPIED", text_color="#3B82F6", font=FONTS["label_md"]).pack(padx=8, pady=2)

        d_body = ctk.CTkFrame(details, fg_color="transparent")
        d_body.pack(fill="x", padx=16, pady=16)
        
        # 2x2 grid for stats
        stats_grid = ctk.CTkFrame(d_body, fg_color="transparent")
        stats_grid.pack(fill="x", pady=(0, 16))
        stats_grid.grid_columnconfigure(0, weight=1)
        stats_grid.grid_columnconfigure(1, weight=1)
        
        s1 = ctk.CTkFrame(stats_grid, fg_color="transparent")
        s1.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ctk.CTkLabel(s1, text="Current Bus", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
        ctk.CTkLabel(s1, text="KL 01 AB 1234", font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(anchor="w")

        s2 = ctk.CTkFrame(stats_grid, fg_color="transparent")
        s2.grid(row=0, column=1, sticky="ew", pady=(0, 12))
        ctk.CTkLabel(s2, text="Assigned Route", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
        ctk.CTkLabel(s2, text="City Center", font=FONTS["body_md"], text_color=COLORS["on_surface"]).pack(anchor="w")

        s3 = ctk.CTkFrame(stats_grid, fg_color="transparent")
        s3.grid(row=1, column=0, sticky="ew")
        ctk.CTkLabel(s3, text="Arrival Time", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
        ctk.CTkLabel(s3, text="10:45:22 AM", font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(anchor="w")

        s4 = ctk.CTkFrame(stats_grid, fg_color="transparent")
        s4.grid(row=1, column=1, sticky="ew")
        ctk.CTkLabel(s4, text="Dwell Time", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
        ctk.CTkLabel(s4, text="14m 30s", font=FONTS["data_mono"], text_color=COLORS["tertiary"]).pack(anchor="w")

        div = ctk.CTkFrame(d_body, fg_color=COLORS["outline_variant"], height=1)
        div.pack(fill="x", pady=12)

        ctk.CTkLabel(d_body, text="Sensor Data", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(0, 8))
        
        for name in ["Cam_A01_Overhead", "Lidar_Zone_A01"]:
            row = ctk.CTkFrame(d_body, fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=4)
            row.pack(fill="x", pady=4)
            r_inner = ctk.CTkFrame(row, fg_color="transparent")
            r_inner.pack(fill="x", padx=8, pady=8)
            ctk.CTkLabel(r_inner, text="📷 " + name, font=FONTS["body_md"], text_color=COLORS["on_surface"]).pack(side="left")
            ctk.CTkLabel(r_inner, text="●", font=("Arial", 14), text_color="#10b981").pack(side="right")

        conf = ctk.CTkFrame(d_body, fg_color=COLORS["surface_bright"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=8)
        conf.pack(fill="x", pady=(12, 0))
        c_inner = ctk.CTkFrame(conf, fg_color="transparent")
        c_inner.pack(fill="x", padx=12, pady=12)
        ctk.CTkLabel(c_inner, text="Detection Confidence", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(side="left")
        ctk.CTkLabel(c_inner, text="98.4%", font=("Inter", 14, "bold"), text_color="#10b981").pack(side="right")

        # Config Preview Panel
        cfg = ctk.CTkFrame(side_panel, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        cfg.pack(fill="x")
        
        c_head = ctk.CTkFrame(cfg, fg_color="transparent")
        c_head.pack(fill="x", padx=16, pady=16)
        ctk.CTkLabel(c_head, text="Detection Zone Preview", font=("Inter", 16, "bold"), text_color=COLORS["on_surface"]).pack(anchor="w")
        
        c_body = ctk.CTkFrame(cfg, fg_color=COLORS["surface_bright"])
        c_body.pack(fill="both", expand=True, padx=1, pady=(0, 1))
        
        feed = ctk.CTkFrame(c_body, fg_color="#213145", border_color=COLORS["outline"], border_width=1, corner_radius=4, height=180)
        feed.pack(fill="x", padx=16, pady=16)
        feed.pack_propagate(False)
        
        tag = ctk.CTkFrame(feed, fg_color="black", corner_radius=4)
        tag.place(x=8, y=8)
        ctk.CTkLabel(tag, text="LIVE: CAM_A01", font=("Inter", 10, "bold"), text_color="white").pack(padx=6, pady=2)
        
        ctk.CTkLabel(feed, text="[ Polygon Overlay Render Area ]", font=FONTS["label_md"], text_color=COLORS["outline_variant"]).place(relx=0.5, rely=0.5, anchor="center")
