import os
import customtkinter as ctk
from PIL import Image
from app.constants import COLORS, FONTS
from app.db.database import get_connection
from app.models.parking_bay_model import ParkingBayModel

class ParkingBayManagementView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.app_controller = app_controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) 

        self.selected_bay = "B02"

        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.grid(row=0, column=0, sticky="nsew")
        self.scroll_container.grid_columnconfigure(0, weight=1)

        self._build_header()
        self.kpi_container = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.kpi_container.grid(row=1, column=0, sticky="ew", padx=32)
        
        self.content_grid = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.content_grid.grid(row=2, column=0, sticky="nsew", padx=32, pady=16)
        self.content_grid.grid_columnconfigure(0, weight=1)
        
        self.term_grid_container = None
        self.side_panel_container = None

        self._refresh_view()

    def _build_header(self):
        header = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 16))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left, text="Parking Bay Management", font=FONTS["headline_lg"], text_color=COLORS["on_surface"]).pack(anchor="w")
        ctk.CTkLabel(left, text="Real-time terminal bay occupancy, camera telemetry and spatial status.", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(
            right, text="🔄 Refresh Bays", font=FONTS["label_md"], 
            fg_color=COLORS["surface_container_high"], text_color=COLORS["primary"],
            border_color=COLORS["outline_variant"], border_width=1, hover_color=COLORS["surface_container_highest"],
            command=self._refresh_view
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            right, text="📍 Configure Detection Zones", font=FONTS["label_md"], 
            fg_color=COLORS["primary"], text_color=COLORS["on_primary"], hover_color=COLORS["primary_container"]
        ).pack(side="left")

    def _refresh_view(self):
        self._build_kpi_cards()
        self._build_terminal_grid(self.content_grid)
        self._build_side_panel(self.content_grid)

    def _build_kpi_cards(self):
        for child in self.kpi_container.winfo_children():
            child.destroy()

        for i in range(5):
            self.kpi_container.grid_columnconfigure(i, weight=1, uniform="kpi")

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM parking_bays")
            total = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM parking_bays WHERE status = 'Available'")
            avail = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM parking_bays WHERE status = 'Occupied'")
            occ = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM parking_bays WHERE status IN ('Maintenance', 'Reserved')")
            maint = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM parking_bays WHERE status = 'Disabled'")
            dis = cur.fetchone()[0]
            conn.close()
        except Exception:
            total, avail, occ, maint, dis = 8, 6, 2, 0, 0

        kpis = [
            {"title": "TOTAL BAYS", "val": str(total), "icon": "⊞", "color": COLORS["outline"], "bg": COLORS["surface_container_lowest"], "accent": None},
            {"title": "AVAILABLE", "val": str(avail), "icon": "✓", "color": "#10b981", "bg": COLORS["surface_container_lowest"], "accent": "#10b981"},
            {"title": "OCCUPIED", "val": str(occ), "icon": "🚌", "color": "#0284c7", "bg": COLORS["surface_container_lowest"], "accent": "#0284c7"},
            {"title": "RESERVED/MAINT", "val": str(maint), "icon": "🔧", "color": "#f59e0b", "bg": COLORS["surface_container_lowest"], "accent": "#f59e0b"},
            {"title": "DISABLED", "val": str(dis), "icon": "⊘", "color": COLORS["error"], "bg": COLORS["surface_container_lowest"], "accent": COLORS["error"]}
        ]

        for i, kpi in enumerate(kpis):
            card = ctk.CTkFrame(self.kpi_container, fg_color=kpi["bg"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12, height=96)
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
        if self.term_grid_container:
            self.term_grid_container.destroy()

        self.term_grid_container = ctk.CTkFrame(parent, fg_color=COLORS["surface"], border_color="#64748b", border_width=2, corner_radius=12)
        self.term_grid_container.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        
        # Header
        header = ctk.CTkFrame(self.term_grid_container, fg_color="#dbe8f8", corner_radius=10)
        header.pack(fill="x", padx=2, pady=2)
        h_inner = ctk.CTkFrame(header, fg_color="transparent")
        h_inner.pack(fill="x", padx=16, pady=12)
        
        ctk.CTkLabel(h_inner, text="Terminal Layout (Ground Bays B01 - B08)", font=("Inter", 14, "bold"), text_color="#0f172a").pack(side="left")
        
        legend = ctk.CTkFrame(h_inner, fg_color="transparent")
        legend.pack(side="right")
        for color, text in [("#10b981", "Available"), ("#0284c7", "Occupied"), ("#f59e0b", "Maintenance"), (COLORS["error"], "Disabled")]:
            ctk.CTkLabel(legend, text="●", text_color=color, font=("Arial", 12)).pack(side="left", padx=(8, 4))
            ctk.CTkLabel(legend, text=text, font=FONTS["label_md"], text_color="#334155").pack(side="left")

        # Grid Content
        border = ctk.CTkFrame(self.term_grid_container, fg_color="#cbd5e1", height=1)
        border.pack(fill="x", padx=2)
        
        grid_area = ctk.CTkFrame(self.term_grid_container, fg_color="transparent")
        grid_area.pack(fill="both", expand=True, padx=16, pady=16)
        
        for i in range(4):
            grid_area.grid_columnconfigure(i, weight=1, uniform="bay")

        bays = ParkingBayModel.get_all_bays()

        for idx, bay in enumerate(bays):
            row_idx = idx // 4
            col_idx = idx % 4
            
            bay_id = bay["bay_id"]
            bay_status = bay["status"]
            v_reg = bay.get("vehicle_reg")
            is_selected = (bay_id == self.selected_bay)
            
            # Determine styles
            border_color = "#0284c7" if is_selected else ("#3b82f6" if bay_status.lower() == "occupied" else "#cbd5e1")
            border_width = 3 if is_selected else (2 if bay_status.lower() == "occupied" else 1)
            accent_color = "#10b981" if bay_status.lower() == "available" else ("#0284c7" if bay_status.lower() == "occupied" else "#f59e0b")

            bay_frame = ctk.CTkFrame(grid_area, fg_color="#ffffff" if is_selected else COLORS["surface_container_lowest"], border_color=border_color, border_width=border_width, corner_radius=10, height=135)
            bay_frame.grid(row=row_idx, column=col_idx, sticky="nsew", padx=8, pady=8)
            bay_frame.pack_propagate(False)

            # Accent stripe
            ctk.CTkFrame(bay_frame, fg_color=accent_color, height=4, corner_radius=0).pack(fill="x")
                
            inner = ctk.CTkFrame(bay_frame, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=12, pady=10)

            # Top Row: Bay ID + Select Click
            top_r = ctk.CTkFrame(inner, fg_color="transparent")
            top_r.pack(fill="x")
            ctk.CTkLabel(top_r, text=f"BAY {bay_id}", font=("Inter", 13, "bold"), text_color=COLORS["on_surface"]).pack(side="left")

            badge_bg = "#dcfce7" if bay_status.lower() == "available" else ("#e0f2fe" if bay_status.lower() == "occupied" else "#fef3c7")
            badge_fg = "#15803d" if bay_status.lower() == "available" else ("#0284c7" if bay_status.lower() == "occupied" else "#b45309")
            ctk.CTkLabel(top_r, text=bay_status.upper(), font=("Inter", 10, "bold"), fg_color=badge_bg, text_color=badge_fg, corner_radius=4).pack(side="right", padx=2, ipadx=4, ipady=1)

            # Center vehicle reg
            if v_reg:
                ctk.CTkLabel(inner, text=f"🚌 {v_reg}", font=("Inter", 12, "bold"), text_color="#0284c7").pack(anchor="w", pady=(8, 2))
                ctk.CTkLabel(inner, text="Ground Docked", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
            else:
                ctk.CTkLabel(inner, text="✓ Empty & Ready", font=FONTS["label_md"], text_color="#10b981").pack(anchor="w", pady=(8, 2))
                ctk.CTkLabel(inner, text="Clear Contact Area", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")

            # Click to select
            btn = ctk.CTkButton(
                inner, text="Select Details ➔" if not is_selected else "● Active View", 
                font=("Inter", 10), height=22,
                fg_color=COLORS["primary"] if is_selected else COLORS["surface_container"],
                text_color=COLORS["on_primary"] if is_selected else COLORS["on_surface"],
                hover_color=COLORS["primary_container"],
                command=lambda b=bay_id: self._select_bay(b)
            )
            btn.pack(side="bottom", fill="x", pady=(4, 0))

    def _build_side_panel(self, parent):
        if self.side_panel_container:
            self.side_panel_container.destroy()

        self.side_panel_container = ctk.CTkFrame(parent, fg_color="transparent", width=360)
        self.side_panel_container.grid(row=0, column=1, sticky="nsew")
        
        # Details Panel
        details = ctk.CTkFrame(self.side_panel_container, fg_color=COLORS["surface_container_lowest"], border_color="#64748b", border_width=2, corner_radius=12)
        details.pack(fill="x", pady=(0, 16))
        
        # Query selected bay
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT bay_id, status, vehicle_reg FROM parking_bays WHERE bay_id = %s", (self.selected_bay,))
        bay_row = cur.fetchone()
        
        current_bus = bay_row[2] if bay_row and bay_row[2] else None
        current_status = bay_row[1] if bay_row else "Available"

        # Query schedule info for this bus
        cur.execute("""
            SELECT s.route, s.destination, s.departure_time, b.driver_name, b.bus_type 
            FROM schedules s
            LEFT JOIN buses b ON b.registration_no = s.bus_no
            WHERE s.bus_no = %s OR s.bay = %s
        """, (current_bus, self.selected_bay))
        sched_row = cur.fetchone()
        conn.close()

        route_name = sched_row[0] if sched_row else "Express Route"
        driver_name = sched_row[3] if sched_row and sched_row[3] else "Fleet Operator"
        dep_time = sched_row[2] if sched_row and sched_row[2] else "--:--"

        d_head = ctk.CTkFrame(details, fg_color="#dbe8f8", corner_radius=10)
        d_head.pack(fill="x", padx=2, pady=2)
        d_h_inner = ctk.CTkFrame(d_head, fg_color="transparent")
        d_h_inner.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(d_h_inner, text=f"Bay Details: {self.selected_bay}", font=("Inter", 14, "bold"), text_color="#0f172a").pack(side="left")
        
        badge_bg = "#e0f2fe" if current_status.lower() == "occupied" else "#dcfce7"
        badge_fg = "#0284c7" if current_status.lower() == "occupied" else "#15803d"
        ctk.CTkLabel(d_h_inner, text=current_status.upper(), text_color=badge_fg, font=("Inter", 11, "bold"), fg_color=badge_bg, corner_radius=4).pack(side="right", padx=2, ipadx=6, ipady=2)

        d_body = ctk.CTkFrame(details, fg_color="transparent")
        d_body.pack(fill="x", padx=16, pady=16)
        
        # Grid stats
        stats_grid = ctk.CTkFrame(d_body, fg_color="transparent")
        stats_grid.pack(fill="x", pady=(0, 16))
        stats_grid.grid_columnconfigure(0, weight=1)
        stats_grid.grid_columnconfigure(1, weight=1)
        
        s1 = ctk.CTkFrame(stats_grid, fg_color="transparent")
        s1.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ctk.CTkLabel(s1, text="Current Vehicle", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
        ctk.CTkLabel(s1, text=current_bus if current_bus else "None (Empty)", font=("Inter", 13, "bold"), text_color=COLORS["primary"] if current_bus else COLORS["on_surface_variant"]).pack(anchor="w")

        s2 = ctk.CTkFrame(stats_grid, fg_color="transparent")
        s2.grid(row=0, column=1, sticky="ew", pady=(0, 12))
        ctk.CTkLabel(s2, text="Assigned Route", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
        ctk.CTkLabel(s2, text=route_name, font=("Inter", 12), text_color=COLORS["on_surface"]).pack(anchor="w")

        s3 = ctk.CTkFrame(stats_grid, fg_color="transparent")
        s3.grid(row=1, column=0, sticky="ew")
        ctk.CTkLabel(s3, text="Driver Name", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
        ctk.CTkLabel(s3, text=driver_name, font=("Inter", 12), text_color=COLORS["on_surface"]).pack(anchor="w")

        s4 = ctk.CTkFrame(stats_grid, fg_color="transparent")
        s4.grid(row=1, column=1, sticky="ew")
        ctk.CTkLabel(s4, text="Departure Time", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
        ctk.CTkLabel(s4, text=dep_time, font=FONTS["data_mono"], text_color=COLORS["tertiary"]).pack(anchor="w")

        div = ctk.CTkFrame(d_body, fg_color="#cbd5e1", height=1)
        div.pack(fill="x", pady=12)

        # Action Buttons
        btn_box = ctk.CTkFrame(d_body, fg_color="transparent")
        btn_box.pack(fill="x", pady=(0, 8))
        
        ctk.CTkButton(
            btn_box, text="⚡ Toggle Occupancy", font=FONTS["label_md"],
            fg_color=COLORS["primary"], text_color=COLORS["on_primary"], hover_color=COLORS["primary_container"],
            command=self._toggle_bay_occupancy
        ).pack(side="left", expand=True, fill="x", padx=(0, 4))

        ctk.CTkButton(
            btn_box, text="Release Bay", font=FONTS["label_md"],
            fg_color="#fee2e2", text_color="#dc2626", hover_color="#fca5a5",
            command=self._release_bay
        ).pack(side="left", expand=True, fill="x", padx=(4, 0))

        # Config Preview Panel
        cfg = ctk.CTkFrame(self.side_panel_container, fg_color=COLORS["surface_container_lowest"], border_color="#64748b", border_width=1, corner_radius=12)
        cfg.pack(fill="x")
        
        c_head = ctk.CTkFrame(cfg, fg_color="transparent")
        c_head.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(c_head, text="CCTV Point-in-Polygon Preview", font=("Inter", 13, "bold"), text_color=COLORS["on_surface"]).pack(anchor="w")
        
        feed = ctk.CTkFrame(cfg, fg_color="#090d16", height=190, corner_radius=6)
        feed.pack(fill="x", padx=12, pady=(0, 12))
        feed.pack_propagate(False)

        preview_img = "live_cctv_annotated.jpg" if os.path.exists("live_cctv_annotated.jpg") else ("test_detection_output.jpg" if os.path.exists("test_detection_output.jpg") else None)
        if preview_img:
            try:
                img = Image.open(preview_img)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(330, 180))
                lbl = ctk.CTkLabel(feed, text="", image=ctk_img)
                lbl.place(relx=0.5, rely=0.5, anchor="center")
            except Exception:
                pass
        
        tag = ctk.CTkFrame(feed, fg_color="#dc2626", corner_radius=4)
        tag.place(x=8, y=8)
        ctk.CTkLabel(tag, text=f"CAM-01 • {self.selected_bay}", font=("Inter", 9, "bold"), text_color="white").pack(padx=6, pady=2)

    def _select_bay(self, bay_id):
        self.selected_bay = bay_id
        self._build_terminal_grid(self.content_grid)
        self._build_side_panel(self.content_grid)

    def _toggle_bay_occupancy(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT status, vehicle_reg FROM parking_bays WHERE bay_id = %s", (self.selected_bay,))
        row = cur.fetchone()
        if row:
            curr_st = row[0]
            new_st = "Available" if curr_st == "Occupied" else "Occupied"
            new_reg = None if new_st == "Available" else "TN 01 AN 2345"
            cur.execute("UPDATE parking_bays SET status = %s, vehicle_reg = %s WHERE bay_id = %s", (new_st, new_reg, self.selected_bay))
            conn.commit()
        conn.close()
        self._refresh_view()

    def _release_bay(self):
        ParkingBayModel.release_bay(self.selected_bay)
        self._refresh_view()
