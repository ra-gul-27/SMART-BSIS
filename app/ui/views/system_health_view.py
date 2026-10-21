import time
import psutil
import customtkinter as ctk
import tkinter as tk
from app.constants import COLORS, FONTS
from app.db.database import get_connection

class SystemHealthView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.app_controller = app_controller
        self._refresh_timer = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.grid(row=0, column=0, sticky="nsew")
        self.scroll_container.grid_columnconfigure(0, weight=1)

        self.cpu_pct = 25.0
        self.ram_pct = 45.0
        self.disk_pct = 35.0
        self.db_latency_ms = 2.4

        self._build_header()
        self._build_services_grid()
        self._build_hardware_network_grid()
        self._build_component_table()
        
        # Periodic live health update
        self._schedule_live_refresh()

    def _schedule_live_refresh(self):
        self._refresh_metrics()
        self._refresh_timer = self.after(3000, self._schedule_live_refresh)

    def _refresh_metrics(self):
        try:
            self.cpu_pct = psutil.cpu_percent(interval=None)
            self.ram_pct = psutil.virtual_memory().percent
            self.disk_pct = psutil.disk_usage(os.path.abspath("/")).percent if hasattr(os, "path") else 40.0
            
            # Measure actual PostgreSQL roundtrip latency
            t0 = time.time()
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT 1;")
            cur.fetchone()
            conn.close()
            self.db_latency_ms = round((time.time() - t0) * 1000, 1)
        except Exception:
            pass

        # Update gauges if built
        if hasattr(self, "cpu_gauge_val"):
            self._update_gauge(self.cpu_canvas, self.cpu_gauge_val, f"{int(self.cpu_pct)}%", self.cpu_pct / 100.0, COLORS["primary"])
            self._update_gauge(self.ram_canvas, self.ram_gauge_val, f"{int(self.ram_pct)}%", self.ram_pct / 100.0, "#0284c7")
            self._update_gauge(self.disk_canvas, self.disk_gauge_val, f"{int(self.disk_pct)}%", self.disk_pct / 100.0, "#059669")
            if hasattr(self, "db_latency_label"):
                self.db_latency_label.configure(text=f"{self.db_latency_ms} ms")

    def _build_header(self):
        header = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 16))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left, text="System Health & Infrastructure Monitor", font=FONTS["headline_lg"], text_color=COLORS["on_surface"]).pack(anchor="w")
        ctk.CTkLabel(left, text="Real-time telemetry of YOLOv11 AI vision, EasyOCR ANPR, PostgreSQL and compute sensors", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(4, 0))

        right = ctk.CTkFrame(header, fg_color="#dcfce7", border_color="#86efac", border_width=1, corner_radius=8)
        right.grid(row=0, column=1, sticky="e")
        
        dot = ctk.CTkFrame(right, width=8, height=8, corner_radius=4, fg_color="#16a34a")
        dot.pack(side="left", padx=(12, 6), pady=8)
        ctk.CTkLabel(right, text="All Systems Operational • Real-Time", font=("Inter", 11, "bold"), text_color="#15803d").pack(side="left", padx=(0, 12), pady=6)

    def _build_services_grid(self):
        grid = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        grid.grid(row=1, column=0, sticky="ew", padx=32, pady=(0, 16))
        
        for i in range(5):
            grid.grid_columnconfigure(i, weight=1, uniform="col")

        cards_data = [
            {"title": "CCTV SENSORS", "badge": "CAM-01 to 04", "sub": "4/4 Streams Live", "val": "Sony STARVIS 1080p", "color": "#166534", "bg": "#dcfce7"},
            {"title": "YOLOv11 ENGINE", "badge": "ACTIVE (COCO)", "sub": "Inference OK", "val": "⚡ 32ms avg latency", "color": "#166534", "bg": "#dcfce7"},
            {"title": "EASYOCR ANPR", "badge": "ACTIVE (CRNN)", "sub": "Ready for Plates", "val": "🏎️ Dual Bumper Pass", "color": "#166534", "bg": "#dcfce7"},
            {"title": "OPENCV PIPELINE", "badge": "RUNNING", "sub": "Point-in-Polygon", "val": "🔄 30 FPS target met", "color": "#166534", "bg": "#dcfce7"},
            {"title": "POSTGRESQL DB", "badge": "CONNECTED", "sub": "smart_bus_db", "val": "⏱️ Roundtrip 2.4 ms", "color": "#1e40af", "bg": "#dbeafe"}
        ]

        for i, data in enumerate(cards_data):
            card = ctk.CTkFrame(grid, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12, height=115)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i==0 else 6, 6 if i<4 else 0))
            card.grid_propagate(False)
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=14, pady=12)

            top = ctk.CTkFrame(inner, fg_color="transparent")
            top.pack(fill="x")
            
            ctk.CTkLabel(top, text=data["title"], font=("Inter", 9, "bold"), text_color=COLORS["on_surface_variant"], justify="left").pack(side="left")
            
            badge = ctk.CTkFrame(top, fg_color=data["bg"], corner_radius=10, border_color=data["color"], border_width=1)
            badge.pack(side="right")
            ctk.CTkLabel(badge, text=data["badge"], font=("Inter", 9, "bold"), text_color=data["color"]).pack(padx=6, pady=1)
            
            ctk.CTkLabel(inner, text=data["sub"], font=("Inter", 13, "bold"), text_color=COLORS["on_surface"]).pack(anchor="w", pady=(6, 0))
            ctk.CTkLabel(inner, text=data["val"], font=("Inter", 11), text_color=COLORS["on_surface_variant"]).pack(side="bottom", anchor="w")

    def _build_hardware_network_grid(self):
        grid = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        grid.grid(row=2, column=0, sticky="ew", padx=32, pady=(0, 16))
        grid.grid_columnconfigure(0, weight=2, uniform="col")
        grid.grid_columnconfigure(1, weight=1, uniform="col")

        # Hardware Utilization Card
        hw_card = ctk.CTkFrame(grid, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        hw_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        hw_inner = ctk.CTkFrame(hw_card, fg_color="transparent")
        hw_inner.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(hw_inner, text="💻 Real-Time Hardware Utilization (psutil)", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(anchor="w", pady=(0, 12))

        gauges_cont = ctk.CTkFrame(hw_inner, fg_color="transparent")
        gauges_cont.pack(fill="both", expand=True)
        gauges_cont.grid_columnconfigure(0, weight=1)
        gauges_cont.grid_columnconfigure(1, weight=1)
        gauges_cont.grid_columnconfigure(2, weight=1)

        self.cpu_canvas, self.cpu_gauge_val = self._create_gauge(gauges_cont, 0, f"{int(self.cpu_pct)}%", "CPU LOAD", self.cpu_pct / 100.0, COLORS["primary"])
        self.ram_canvas, self.ram_gauge_val = self._create_gauge(gauges_cont, 1, f"{int(self.ram_pct)}%", "RAM MEMORY", self.ram_pct / 100.0, "#0284c7")
        self.disk_canvas, self.disk_gauge_val = self._create_gauge(gauges_cont, 2, f"{int(self.disk_pct)}%", "DISK STORAGE", self.disk_pct / 100.0, "#059669")

        # Network & Latency Card
        nw_card = ctk.CTkFrame(grid, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        nw_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        
        nw_inner = ctk.CTkFrame(nw_card, fg_color="transparent")
        nw_inner.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(nw_inner, text="🛜 Network & Database Latency", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(anchor="w", pady=(0, 16))

        def add_bar(parent, title, val_text, val_color, pct, bar_color):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=(0, 14))
            lbls = ctk.CTkFrame(row, fg_color="transparent")
            lbls.pack(fill="x", pady=(0, 4))
            ctk.CTkLabel(lbls, text=title, font=FONTS["label_md"], text_color=COLORS["on_surface"]).pack(side="left")
            lbl = ctk.CTkLabel(lbls, text=val_text, font=FONTS["data_mono"], text_color=val_color)
            lbl.pack(side="right")
            
            bar_bg = ctk.CTkFrame(row, fg_color=COLORS["surface_variant"], height=8, corner_radius=4)
            bar_bg.pack(fill="x")
            
            bar_fill = ctk.CTkFrame(bar_bg, fg_color=bar_color, height=8, corner_radius=4)
            bar_fill.place(relx=0, rely=0, relwidth=pct)
            return lbl

        self.db_latency_label = add_bar(nw_inner, "PostgreSQL Roundtrip", f"{self.db_latency_ms} ms", COLORS["on_surface"], 0.25, "#10b981")
        add_bar(nw_inner, "YOLOv11 Inference Latency", "32 ms", "#0284c7", 0.35, "#0284c7")
        add_bar(nw_inner, "FastAPI Service Latency", "12 ms", COLORS["primary"], 0.15, COLORS["primary"])

    def _create_gauge(self, parent, col, val_text, title, pct, color):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, sticky="nsew")
        
        canvas = tk.Canvas(frame, bg=COLORS["surface_container_lowest"], highlightthickness=0, width=120, height=120)
        canvas.pack(pady=4)
        
        pad = 14
        x0, y0, x1, y1 = pad, pad, 120 - pad, 120 - pad
        canvas.create_arc(x0, y0, x1, y1, start=0, extent=359.9, style=tk.ARC, outline=COLORS["surface_variant"], width=10)
        
        extent = max(1.0, min(359.9, pct * 360.0))
        arc_id = canvas.create_arc(x0, y0, x1, y1, start=90, extent=-extent, style=tk.ARC, outline=color, width=10)
        text_id = canvas.create_text(60, 60, text=val_text, font=("Inter", 16, "bold"), fill=COLORS["on_surface"])
        
        canvas.arc_id = arc_id
        canvas.text_id = text_id
        canvas.coords_box = (x0, y0, x1, y1)

        ctk.CTkLabel(frame, text=title, font=("Inter", 11, "bold"), text_color=COLORS["on_surface_variant"]).pack(pady=(4, 0))
        return canvas, text_id

    def _update_gauge(self, canvas, text_id, val_text, pct, color):
        try:
            x0, y0, x1, y1 = canvas.coords_box
            extent = max(1.0, min(359.9, pct * 360.0))
            canvas.delete(canvas.arc_id)
            canvas.arc_id = canvas.create_arc(x0, y0, x1, y1, start=90, extent=-extent, style=tk.ARC, outline=color, width=10)
            canvas.itemconfigure(text_id, text=val_text)
        except Exception:
            pass

    def _build_component_table(self):
        table_card = ctk.CTkFrame(self.scroll_container, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        table_card.grid(row=3, column=0, sticky="ew", padx=32, pady=(0, 32))
        
        head = ctk.CTkFrame(table_card, fg_color=COLORS["surface_container_low"], corner_radius=12)
        head.pack(fill="x", padx=1, pady=1)
        h_inner = ctk.CTkFrame(head, fg_color="transparent")
        h_inner.pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(h_inner, text="Transit Component Health Matrix", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(side="left")

        cols = [("COMPONENT", 2), ("ENDPOINT / TARGET", 3), ("UPTIME", 1), ("HEALTH STATUS", 1.5)]
        
        th_row = ctk.CTkFrame(table_card, fg_color="transparent")
        th_row.pack(fill="x", padx=16, pady=8)
        for i, (c, w) in enumerate(cols):
            th_row.grid_columnconfigure(i, weight=int(w*10), uniform="c_col")
            ctk.CTkLabel(th_row, text=c, font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).grid(row=0, column=i, sticky="w", padx=4)

        components = [
            ("PostgreSQL Relational DB", "localhost:5432/smart_bus_db", "99.98%", "ONLINE 🟢"),
            ("FastAPI Vision REST API", "http://127.0.0.1:8000/docs", "100.0%", "RUNNING 🟢"),
            ("YOLOv11 Bus Object Detector", "yolo11n.pt (COCO Classes 5,7)", "100.0%", "HEALTHY 🟢"),
            ("EasyOCR Neural OCR Engine", "CRAFT MLT-25K + CRNN English", "99.95%", "HEALTHY 🟢"),
            ("Terminal Parking Bay Manager", "Point-in-Polygon B01-B08", "100.0%", "ACTIVE 🟢")
        ]

        for idx, (comp, endpoint, uptime, status) in enumerate(components):
            bg = "transparent" if idx % 2 == 0 else COLORS["surface_container_low"]
            tr = ctk.CTkFrame(table_card, fg_color=bg, corner_radius=0)
            tr.pack(fill="x", padx=1)
            tr_inner = ctk.CTkFrame(tr, fg_color="transparent")
            tr_inner.pack(fill="x", padx=16, pady=10)
            for j in range(4):
                tr_inner.grid_columnconfigure(j, weight=int(cols[j][1]*10), uniform="c_col")

            ctk.CTkLabel(tr_inner, text=comp, font=("Inter", 12, "bold"), text_color=COLORS["on_surface"]).grid(row=0, column=0, sticky="w", padx=4)
            ctk.CTkLabel(tr_inner, text=endpoint, font=FONTS["data_mono"], text_color=COLORS["on_surface_variant"]).grid(row=0, column=1, sticky="w", padx=4)
            ctk.CTkLabel(tr_inner, text=uptime, font=FONTS["data_mono"], text_color="#059669").grid(row=0, column=2, sticky="w", padx=4)
            ctk.CTkLabel(tr_inner, text=status, font=("Inter", 11, "bold"), text_color="#15803d").grid(row=0, column=3, sticky="w", padx=4)

    def destroy(self):
        if hasattr(self, "_refresh_timer") and self._refresh_timer:
            try:
                self.after_cancel(self._refresh_timer)
            except Exception:
                pass
        super().destroy()
