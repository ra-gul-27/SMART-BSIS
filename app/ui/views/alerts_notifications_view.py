import customtkinter as ctk
from app.constants import COLORS, FONTS

class AlertsNotificationsView(ctk.CTkFrame):
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
        self.content_grid.grid_columnconfigure(0, weight=1)
        
        self._build_table_panel(self.content_grid)

    def _build_header(self):
        header = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 16))
        
        ctk.CTkLabel(header, text="Alerts & Notifications", font=FONTS["headline_lg"], text_color=COLORS["on_surface"]).pack(anchor="w")
        ctk.CTkLabel(header, text="Monitor operational and AI system alerts", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")

    def _build_kpi_cards(self):
        kpi_container = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        kpi_container.grid(row=1, column=0, sticky="ew", padx=32)
        
        # 4 columns
        for i in range(4):
            kpi_container.grid_columnconfigure(i, weight=1, uniform="kpi")

        kpis = [
            {"title": "TOTAL ALERTS", "val": "7", "sub": "Last 24 hours", "color": COLORS["primary"], "border": COLORS["outline_variant"], "bg": COLORS["surface"]},
            {"title": "CRITICAL", "val": "2", "sub": "Requires immediate action", "color": COLORS["error"], "border": "#fca5a5", "bg": COLORS["surface"]},
            {"title": "WARNINGS", "val": "3", "sub": "Monitor closely", "color": "#f59e0b", "border": "#fcd34d", "bg": COLORS["surface"]},
            {"title": "RESOLVED", "val": "12", "sub": "Cleared today", "color": COLORS["on_surface"], "border": COLORS["outline_variant"], "bg": COLORS["surface"]}
        ]

        for i, kpi in enumerate(kpis):
            card = ctk.CTkFrame(kpi_container, fg_color=kpi["bg"], border_color=kpi["border"], border_width=1, corner_radius=12, height=120)
            card.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 8, 0 if i == 3 else 8))
            card.pack_propagate(False)
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=16, pady=16)

            ctk.CTkLabel(inner, text=kpi["title"], font=("Inter", 12, "bold"), text_color=kpi["color"] if kpi["color"] != COLORS["on_surface"] else COLORS["on_surface_variant"]).pack(anchor="w")
            ctk.CTkLabel(inner, text=kpi["val"], font=("Inter", 32, "bold"), text_color=kpi["color"]).pack(anchor="w", pady=(4, 8))
            ctk.CTkLabel(inner, text=kpi["sub"], font=("Inter", 11), text_color=kpi["color"] if kpi["color"] != COLORS["on_surface"] else COLORS["on_surface_variant"]).pack(anchor="w")

    def _build_table_panel(self, parent):
        table_card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        table_card.grid(row=0, column=0, sticky="nsew")
        
        # Header Row
        thead = ctk.CTkFrame(table_card, fg_color=COLORS["surface_container_lowest"], corner_radius=12)
        thead.pack(fill="x", padx=1, pady=1)
        th_inner = ctk.CTkFrame(thead, fg_color="transparent")
        th_inner.pack(fill="x", padx=16, pady=16)
        
        ctk.CTkLabel(th_inner, text="Active Alerts Feed", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(side="left")
        ctk.CTkButton(th_inner, text="🔍 Filter", font=FONTS["label_md"], width=80, fg_color="transparent", border_color=COLORS["outline_variant"], border_width=1, text_color=COLORS["on_surface"], hover_color=COLORS["surface_container"]).pack(side="right")

        border1 = ctk.CTkFrame(table_card, fg_color=COLORS["outline_variant"], height=1)
        border1.pack(fill="x", padx=1)

        # Col headers
        cols = [
            ("ICON", 0.3), ("TYPE / TIMESTAMP", 1.2), ("DETAILS", 3.5), ("ACTIONS", 2.0)
        ]
        
        th_row = ctk.CTkFrame(table_card, fg_color=COLORS["surface_container_low"])
        th_row.pack(fill="x", padx=1)
        th_r_inner = ctk.CTkFrame(th_row, fg_color="transparent")
        th_r_inner.pack(fill="x", padx=16, pady=8)

        for i, (c, w) in enumerate(cols):
            th_r_inner.grid_columnconfigure(i, weight=int(w*10), uniform="col")
            anchor = "w" if i < len(cols) - 1 else "e"
            sticky = "w" if anchor == "w" else "e"
            ctk.CTkLabel(th_r_inner, text=c if c != "ICON" else "", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).grid(row=0, column=i, sticky=sticky, padx=4)

        border2 = ctk.CTkFrame(table_card, fg_color=COLORS["outline_variant"], height=1)
        border2.pack(fill="x", padx=1)

        # Table Body
        data = [
            {
                "type": "CRITICAL", "ts": "10:30 AM", "title": "Camera 04 Offline", "desc": "Main entrance ANPR camera has lost connection to the server.", 
                "bg": "#fefcfc", "icon": "❌", "icon_col": COLORS["error"], "badge_bg": COLORS["error"], "badge_fg": "white",
                "actions": [("Diagnose", "secondary"), ("Resolve", "primary")]
            },
            {
                "type": "BAY CONFLICT", "ts": "10:15 AM", "title": "Bay B12 - Multiple buses detected", "desc": "ANPR detected TN 01 AN 2345 and TN 01 AP 1284 in the same bay area.", 
                "bg": "#fcfbfa", "icon": "🚌", "icon_col": "#b75b00", "badge_bg": "#b75b00", "badge_fg": "white",
                "actions": [("View Cameras", "tertiary"), ("Reassign Bay", "surface")]
            },
            {
                "type": "UNKNOWN BUS", "ts": "09:42 AM", "title": "Unknown registration detected", "desc": "A vehicle not found in the daily manifest entered via North Gate.", 
                "bg": COLORS["surface_container_lowest"], "icon": "❓", "icon_col": COLORS["outline"], "badge_bg": COLORS["surface_variant"], "badge_fg": COLORS["on_surface_variant"],
                "actions": [("View Cameras", "tertiary"), ("Resolve", "primary")]
            }
        ]

        for i, row in enumerate(data):
            tr = ctk.CTkFrame(table_card, fg_color=row["bg"], corner_radius=0)
            tr.pack(fill="x", padx=1)
            
            tr_content = ctk.CTkFrame(tr, fg_color="transparent")
            tr_content.pack(fill="x", padx=16, pady=16)
            
            for j, (c, w) in enumerate(cols):
                tr_content.grid_columnconfigure(j, weight=int(w*10), uniform="col")

            # Col 1: Icon
            c1 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c1.grid(row=0, column=0, sticky="ew", padx=4)
            ctk.CTkLabel(c1, text=row["icon"], font=("Arial", 20), text_color=row["icon_col"]).pack(anchor="n", pady=4)

            # Col 2: Type / Timestamp
            c2 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c2.grid(row=0, column=1, sticky="ew", padx=4)
            badge = ctk.CTkFrame(c2, fg_color=row["badge_bg"], corner_radius=12)
            badge.pack(anchor="w", pady=(2, 4))
            ctk.CTkLabel(badge, text=row["type"], font=("Inter", 9, "bold"), text_color=row["badge_fg"]).pack(padx=8, pady=0)
            ctk.CTkLabel(c2, text=row["ts"], font=FONTS["data_mono"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", padx=2)

            # Col 3: Details
            c3 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c3.grid(row=0, column=2, sticky="ew", padx=4)
            ctk.CTkLabel(c3, text=row["title"], font=("Inter", 14, "bold"), text_color=COLORS["on_surface"]).pack(anchor="w")
            ctk.CTkLabel(c3, text=row["desc"], font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(2, 0))

            # Col 4: Actions
            c4 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c4.grid(row=0, column=3, sticky="ew", padx=4)
            act_wrapper = ctk.CTkFrame(c4, fg_color="transparent")
            act_wrapper.pack(anchor="e")
            
            for act_name, act_style in row["actions"]:
                if act_style == "primary":
                    fg = COLORS["primary"]
                    tc = "white"
                    bc = COLORS["primary"]
                    hover = COLORS["primary_container"]
                elif act_style == "secondary":
                    fg = "white"
                    tc = COLORS["primary"]
                    bc = COLORS["primary"]
                    hover = COLORS["surface_container"]
                elif act_style == "surface":
                    fg = COLORS["surface_variant"]
                    tc = COLORS["on_surface"]
                    bc = COLORS["outline_variant"]
                    hover = COLORS["surface_container_high"]
                else: # tertiary
                    fg = "transparent"
                    tc = COLORS["on_surface_variant"]
                    bc = COLORS["outline_variant"]
                    hover = COLORS["surface_container"]

                ctk.CTkButton(act_wrapper, text=act_name, font=FONTS["label_md"], fg_color=fg, border_color=bc, border_width=1, text_color=tc, hover_color=hover, width=80, height=28).pack(side="left", padx=(8, 0))

            if i < len(data) - 1:
                border = ctk.CTkFrame(table_card, fg_color=COLORS["outline_variant"], height=1)
                border.pack(fill="x", padx=1)
