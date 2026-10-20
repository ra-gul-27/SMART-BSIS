import customtkinter as ctk
import tkinter as tk
from app.constants import COLORS, FONTS

class SystemHealthView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.app_controller = app_controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.grid(row=0, column=0, sticky="nsew")
        self.scroll_container.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_services_grid()
        self._build_hardware_network_grid()
        self._build_table()

    def _build_header(self):
        header = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 16))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left, text="System Health Monitor", font=FONTS["headline_lg"], text_color=COLORS["on_surface"]).pack(anchor="w")
        ctk.CTkLabel(left, text="Real-time status of critical transit infrastructure components.", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(4, 0))

        right = ctk.CTkFrame(header, fg_color=COLORS["surface_container"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=8)
        right.grid(row=0, column=1, sticky="e")
        right.grid_columnconfigure(1, weight=1)
        
        # Pulsing dot simulation (just a green dot)
        dot = ctk.CTkFrame(right, width=8, height=8, corner_radius=4, fg_color="#22c55e")
        dot.grid(row=0, column=0, padx=(12, 8), pady=8)
        ctk.CTkLabel(right, text="All Systems Operational", font=FONTS["data_mono"], text_color=COLORS["on_surface"]).grid(row=0, column=1, padx=(0, 12), pady=8)

    def _build_services_grid(self):
        grid = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        grid.grid(row=1, column=0, sticky="ew", padx=32, pady=(0, 16))
        # 5 columns
        for i in range(5):
            grid.grid_columnconfigure(i, weight=1, uniform="col")

        cards_data = [
            {"title": "CCTV\nCameras", "icon": "📷", "badge": "6/6 Online", "sub": "check_circle", "type": "bar", "val": 1.0, "color": "#22c55e"},
            {"title": "YOLOv11\nEngine", "icon": "👁️", "badge": "ACTIVE", "sub": "Inference OK", "type": "text", "val": "⚡ 42ms avg latency", "color": "#166534", "bg": "#dcfce7"},
            {"title": "ANPR\nService", "icon": "🚗", "badge": "ACTIVE", "sub": "Processing", "type": "text", "val": "🏎️ 120 plates/min", "color": "#166534", "bg": "#dcfce7"},
            {"title": "OpenCV\nStream", "icon": "🎞️", "badge": "RUNNING", "sub": "Stable", "type": "text", "val": "🔄 30 FPS target met", "color": "#166534", "bg": "#dcfce7"},
            {"title": "PostgreSQL\nDB", "icon": "💾", "badge": "CONNECTED", "sub": "Synced", "type": "text", "val": "⏱️ Last updated just now", "color": "#1e40af", "bg": "#dbeafe"}
        ]

        for i, data in enumerate(cards_data):
            card = ctk.CTkFrame(grid, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12, height=120)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i==0 else 8, 8 if i<4 else 0))
            card.grid_propagate(False)
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=16, pady=16)

            top = ctk.CTkFrame(inner, fg_color="transparent")
            top.pack(fill="x")
            
            ctk.CTkLabel(top, text=data["title"], font=FONTS["label_md"], text_color=COLORS["on_surface_variant"], justify="left").pack(side="left")
            
            if data["type"] == "bar":
                ctk.CTkLabel(top, text="✔", text_color="#16a34a").pack(side="right")
                ctk.CTkLabel(inner, text=data["badge"], font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(anchor="w", pady=(8, 0))
                
                bar_cont = ctk.CTkFrame(inner, fg_color=COLORS["surface_variant"], height=4, corner_radius=2)
                bar_cont.pack(fill="x", side="bottom")
                bar_cont.pack_propagate(False)
                bar_fill = ctk.CTkFrame(bar_cont, fg_color="#22c55e", width=200, corner_radius=2)
                bar_fill.pack(side="left", fill="y")
            else:
                badge = ctk.CTkFrame(top, fg_color=data["bg"], corner_radius=12, border_color=data["color"], border_width=1)
                badge.pack(side="right")
                ctk.CTkLabel(badge, text=data["badge"], font=("Inter", 10, "bold"), text_color=data["color"]).pack(padx=8, pady=2)
                
                ctk.CTkLabel(inner, text=data["sub"], font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(anchor="w", pady=(8, 0))
                ctk.CTkLabel(inner, text=data["val"], font=("Inter", 12), text_color=COLORS["on_surface_variant"]).pack(side="bottom", anchor="w")

    def _build_hardware_network_grid(self):
        grid = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        grid.grid(row=2, column=0, sticky="ew", padx=32, pady=(0, 16))
        grid.grid_columnconfigure(0, weight=2, uniform="col")
        grid.grid_columnconfigure(1, weight=1, uniform="col")

        hw_card = ctk.CTkFrame(grid, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        hw_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        hw_inner = ctk.CTkFrame(hw_card, fg_color="transparent")
        hw_inner.pack(fill="both", expand=True, padx=24, pady=24)
        ctk.CTkLabel(hw_inner, text="💻 Hardware Utilization", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(0, 16))

        gauges_cont = ctk.CTkFrame(hw_inner, fg_color="transparent")
        gauges_cont.pack(fill="both", expand=True)
        gauges_cont.grid_columnconfigure(0, weight=1)
        gauges_cont.grid_columnconfigure(1, weight=1)
        gauges_cont.grid_columnconfigure(2, weight=1)

        self._build_gauge(gauges_cont, 0, "45%", "CPU", 0.45, COLORS["primary"])
        self._build_gauge(gauges_cont, 1, "78%", "GPU", 0.78, "#d97706") # amber-600
        self._build_gauge(gauges_cont, 2, "62%", "RAM", 0.62, COLORS["primary"])

        nw_card = ctk.CTkFrame(grid, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        nw_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        
        nw_inner = ctk.CTkFrame(nw_card, fg_color="transparent")
        nw_inner.pack(fill="both", expand=True, padx=24, pady=24)
        ctk.CTkLabel(nw_inner, text="🛜 Network & Latency", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(0, 16))

        def add_bar(parent, title, val_text, val_color, pct, bar_color):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=(0, 16))
            lbls = ctk.CTkFrame(row, fg_color="transparent")
            lbls.pack(fill="x", pady=(0, 4))
            ctk.CTkLabel(lbls, text=title, font=FONTS["label_md"], text_color=COLORS["on_surface"]).pack(side="left")
            ctk.CTkLabel(lbls, text=val_text, font=FONTS["data_mono"], text_color=val_color).pack(side="right")
            
            bar_bg = ctk.CTkFrame(row, fg_color=COLORS["surface_variant"], height=8, corner_radius=4)
            bar_bg.pack(fill="x")
            
            # Use place for proportional width
            bar_fill = ctk.CTkFrame(bar_bg, fg_color=bar_color, height=8, corner_radius=4)
            bar_fill.place(relx=0, rely=0, relwidth=pct)

        add_bar(nw_inner, "API Response Time", "120ms", COLORS["on_surface"], 0.25, COLORS["primary"])
        add_bar(nw_inner, "Inference Latency", "42ms", "#d97706", 0.4, "#f59e0b")
        add_bar(nw_inner, "Global FPS Avg", "29.5", COLORS["on_surface"], 0.95, "#22c55e")

    def _build_gauge(self, parent, col, val_text, title, pct, color):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, sticky="nsew")
        
        canvas = tk.Canvas(frame, bg=COLORS["surface_container_lowest"], highlightthickness=0, width=130, height=130)
        canvas.pack(pady=10)
        
        w = 130
        h = 130
        pad = 16
        x0, y0 = pad, pad
        x1, y1 = w - pad, h - pad
        
        # draw track circle
        canvas.create_arc(x0, y0, x1, y1, start=0, extent=359.9, style=tk.ARC, outline=COLORS["surface_variant"], width=12)
        # draw progress
        # starts at top: 90 degrees
        extent = -(pct * 359.9)
        canvas.create_arc(x0, y0, x1, y1, start=90, extent=extent, style=tk.ARC, outline=color, width=12)
        
        canvas.create_text(w/2, h/2 - 10, text=val_text, font=("Inter", 24, "bold"), fill=color if color != COLORS["primary"] else COLORS["on_surface"])
        canvas.create_text(w/2, h/2 + 15, text=title, font=FONTS["label_md"], fill=COLORS["on_surface_variant"])

    def _build_table(self):
        # Wrapper frame to guarantee a visible border (children in CTkFrame can cover borders)
        table_border = ctk.CTkFrame(self.scroll_container, fg_color="#94a3b8", corner_radius=12)
        table_border.grid(row=3, column=0, sticky="ew", padx=32, pady=(0, 32))
        
        # Inner card
        table_card = ctk.CTkFrame(table_border, fg_color=COLORS["surface_container_lowest"], corner_radius=11)
        table_card.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Solid header
        header = ctk.CTkFrame(table_card, fg_color=COLORS["surface_container_low"], corner_radius=11)
        header.pack(fill="x")
        
        title_row = ctk.CTkFrame(header, fg_color="transparent")
        title_row.pack(fill="x", padx=16, pady=(12, 0))
        ctk.CTkLabel(title_row, text="Edge Device Node Status", font=("Arial", 16, "bold"), text_color="#1e293b").pack(side="left")
        ctk.CTkButton(title_row, text="🔄 Refresh", font=FONTS["label_md"], fg_color="transparent", text_color=COLORS["primary"], hover_color=COLORS["primary_container"], width=80).pack(side="right")
        
        # Mask bottom corners to connect with the table body seamlessly
        bottom_mask = ctk.CTkFrame(header, fg_color=COLORS["surface_container_low"], height=12, corner_radius=0)
        bottom_mask.pack(side="bottom", fill="x")
        
        # Dark Border directly under the header
        ctk.CTkFrame(table_card, fg_color="#cbd5e1", height=2).pack(fill="x")
        
        # table header
        th = ctk.CTkFrame(table_card, fg_color=COLORS["surface"])
        th.pack(fill="x")
        
        cols = [
            ("Location / ID", 3),
            ("Status", 2),
            ("FPS", 1),
            ("Latency", 1),
            ("Last Frame Recv", 2),
            ("Actions", 1)
        ]
        
        for i, (text, weight) in enumerate(cols):
            th.grid_columnconfigure(i, weight=weight, uniform="col")
            lbl_anchor = "w" if i < len(cols)-1 else "e"
            # Exactly matching the font, boldness, and deep blue-grey color from the screenshot
            ctk.CTkLabel(th, text=text.upper(), font=("Segoe UI", 12, "bold"), text_color="#1e40af", anchor=lbl_anchor).grid(row=0, column=i, sticky="ew", padx=16, pady=10)
            
        # Darker Border under table header
        ctk.CTkFrame(table_card, fg_color="#cbd5e1", height=2).pack(fill="x")
            
        data = [
            {"loc_icon": "📹", "loc": "Bay 1 Entry (CAM-01)", "status": "● Operational", "st_border": "#bbf7d0", "st_text": "#15803d", "st_bg": "#f0fdf4", "icon_c": COLORS["surface_variant"], "fps": "30.0", "lat": "38ms", "last": "2s ago", "bg": "transparent"},
            {"loc_icon": "📹", "loc": "Bay 2 Exit (CAM-02)", "status": "● Operational", "st_border": "#bbf7d0", "st_text": "#15803d", "st_bg": "#f0fdf4", "icon_c": COLORS["surface_variant"], "fps": "29.8", "lat": "41ms", "last": "1s ago", "bg": COLORS["surface"]},
            {"loc_icon": "📹", "loc": "Passenger Area A (CAM-03)", "status": "● Warning", "st_border": "#fde68a", "st_text": "#9a3412", "st_bg": "#fffbeb", "icon_c": "#f59e0b", "fps": "22.4 ↓", "fps_color": "#d97706", "lat": "85ms", "lat_color": "#d97706", "last": "4s ago", "bg": "transparent"},
            {"loc_icon": "📹", "loc": "Ticketing Zone (CAM-04)", "status": "● Operational", "st_border": "#bbf7d0", "st_text": "#15803d", "st_bg": "#f0fdf4", "icon_c": COLORS["surface_variant"], "fps": "30.0", "lat": "39ms", "last": "1s ago", "bg": COLORS["surface"]}
        ]
        
        for r_idx, row in enumerate(data):
            bg = row.get("bg", "transparent")
            tr = ctk.CTkFrame(table_card, fg_color=bg, corner_radius=0)
            tr.pack(fill="x")
            
            for i, (text, weight) in enumerate(cols):
                tr.grid_columnconfigure(i, weight=weight, uniform="col")
                
                cell = ctk.CTkFrame(tr, fg_color="transparent")
                cell.grid(row=0, column=i, sticky="ew", padx=16, pady=10)
                
                if i == 0:
                    loc_cont = ctk.CTkFrame(cell, fg_color="transparent")
                    loc_cont.pack(anchor="w")
                    ctk.CTkLabel(loc_cont, text=row["loc_icon"], text_color=row["icon_c"], font=("Arial", 16)).pack(side="left", padx=(0, 6))
                    ctk.CTkLabel(loc_cont, text=row["loc"], font=("Arial", 12), text_color="#1e293b").pack(side="left")
                elif i == 1:
                    badge = ctk.CTkFrame(cell, fg_color=row["st_bg"], corner_radius=12, border_color=row["st_border"], border_width=1)
                    badge.pack(anchor="w")
                    ctk.CTkLabel(badge, text=row["status"], font=("Arial", 11, "bold"), text_color=row["st_text"]).pack(padx=8, pady=2)
                elif i == 2:
                    color = row.get("fps_color", "#1e293b")
                    ctk.CTkLabel(cell, text=row["fps"], font=("Arial", 12), text_color=color).pack(anchor="w")
                elif i == 3:
                    color = row.get("lat_color", "#1e293b")
                    ctk.CTkLabel(cell, text=row["lat"], font=("Arial", 12), text_color=color).pack(anchor="w")
                elif i == 4:
                    ctk.CTkLabel(cell, text=row["last"], font=("Arial", 12), text_color="#475569").pack(anchor="w")
                elif i == 5:
                    # Enlarge action buttons for better visibility
                    ctk.CTkButton(cell, text="⋮", font=("Arial", 24, "bold"), fg_color="transparent", text_color="#1e293b", width=40, hover_color=COLORS["surface_container"]).pack(anchor="e")
                    
            if r_idx < len(data) - 1:
                # 2px divider between rows to guarantee visibility
                divider = ctk.CTkFrame(table_card, fg_color="#cbd5e1", height=2)
                divider.pack(fill="x")
