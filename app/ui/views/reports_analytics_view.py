import customtkinter as ctk
import tkinter as tk
from app.constants import COLORS, FONTS

class ReportsAnalyticsView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.app_controller = app_controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) 

        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.grid(row=0, column=0, sticky="nsew")
        self.scroll_container.grid_columnconfigure(0, weight=1)

        self._build_header()
        
        self.grid_container = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.grid_container.grid(row=1, column=0, sticky="nsew", padx=32, pady=16)
        self.grid_container.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_container.grid_columnconfigure(1, weight=1, uniform="col")
        self.grid_container.grid_columnconfigure(2, weight=1, uniform="col")
        
        self._build_bus_arrivals(self.grid_container, row=0, col=0, colspan=2)
        self._build_anpr(self.grid_container, row=0, col=2, colspan=1)
        self._build_yolo(self.grid_container, row=1, col=0, colspan=1)
        self._build_parking(self.grid_container, row=1, col=1, colspan=2)

    def _build_header(self):
        header = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 16))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left, text="Reports & Analytics", font=FONTS["headline_lg"], text_color=COLORS["on_surface"]).pack(anchor="w")
        ctk.CTkLabel(left, text="Analyze bus-stand operations and AI performance", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e", pady=(16, 0))

        # Date Segments
        dates = ctk.CTkFrame(right, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=8)
        dates.pack(side="left", padx=(0, 16))
        
        ctk.CTkButton(dates, text="Today", fg_color="transparent", text_color=COLORS["on_surface_variant"], width=60, hover_color=COLORS["surface_container_low"]).pack(side="left", padx=2, pady=2)
        ctk.CTkButton(dates, text="Yesterday", fg_color="transparent", text_color=COLORS["on_surface_variant"], width=80, hover_color=COLORS["surface_container_low"]).pack(side="left", padx=2, pady=2)
        ctk.CTkButton(dates, text="7 Days", fg_color=COLORS["primary"], text_color=COLORS["on_primary"], width=60).pack(side="left", padx=2, pady=2)
        ctk.CTkButton(dates, text="30 Days", fg_color="transparent", text_color=COLORS["on_surface_variant"], width=70, hover_color=COLORS["surface_container_low"]).pack(side="left", padx=2, pady=2)

        # Export Buttons
        ctk.CTkButton(right, text="📄 Export PDF", fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, text_color=COLORS["on_surface"], hover_color=COLORS["surface_container_low"], width=110).pack(side="left", padx=(0, 8))
        ctk.CTkButton(right, text="📊 Export CSV", fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, text_color=COLORS["on_surface"], hover_color=COLORS["surface_container_low"], width=110).pack(side="left", padx=(0, 8))
        ctk.CTkButton(right, text="🖨️", fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, text_color=COLORS["on_surface"], hover_color=COLORS["surface_container_low"], width=40).pack(side="left")

    def _build_bus_arrivals(self, parent, row, col, colspan):
        card = ctk.CTkFrame(parent, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12, height=320)
        card.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=(0, 16), pady=(0, 16))
        card.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=24)

        head = ctk.CTkFrame(inner, fg_color="transparent")
        head.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(head, text="Bus Arrivals Per Hour", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(side="left")
        ctk.CTkLabel(head, text="⋮", font=("Arial", 20), text_color=COLORS["on_surface_variant"]).pack(side="right")

        # Chart area
        chart = ctk.CTkFrame(inner, fg_color="transparent", border_color=COLORS["outline_variant"])
        chart.pack(fill="both", expand=True)
        # Left and Bottom borders for axis
        axis = ctk.CTkFrame(chart, fg_color="transparent")
        axis.pack(fill="both", expand=True, pady=(0, 24))
        
        # We will use place to position bars at the bottom
        bars_container = ctk.CTkFrame(axis, fg_color="transparent")
        bars_container.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # 12 bars
        data = [20, 45, 85, 70, 40, 35, 50, 45, 60, 75, 55, 30]
        max_val = 100
        n = len(data)
        
        for i, val in enumerate(data):
            h_pct = val / max_val
            color = COLORS["primary"] if val > 55 else COLORS["primary_container"]
            bar = ctk.CTkFrame(bars_container, fg_color=color, corner_radius=4)
            # Center each bar in its slice
            slice_w = 1.0 / n
            bar_w = slice_w * 0.8 # 80% of slice width
            margin = slice_w * 0.1
            bar.place(relx=(i * slice_w) + margin, rely=1.0 - h_pct, relwidth=bar_w, relheight=h_pct)
            
        bottom_line = ctk.CTkFrame(chart, fg_color=COLORS["outline_variant"], height=1)
        bottom_line.place(relx=0, rely=1.0, y=-24, relwidth=1)
        left_line = ctk.CTkFrame(chart, fg_color=COLORS["outline_variant"], width=1)
        left_line.place(relx=0, rely=0, relheight=1)

        labels = ctk.CTkFrame(chart, fg_color="transparent", height=24)
        labels.place(relx=0, rely=1.0, y=-20, relwidth=1)
        ctk.CTkLabel(labels, text="06:00", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).place(relx=0, anchor="nw")
        ctk.CTkLabel(labels, text="12:00", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).place(relx=0.5, anchor="n")
        ctk.CTkLabel(labels, text="18:00", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).place(relx=1.0, anchor="ne")

    def _build_anpr(self, parent, row, col, colspan):
        card = ctk.CTkFrame(parent, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12, height=320)
        card.grid(row=row, column=col, columnspan=colspan, sticky="nsew", pady=(0, 16))
        card.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=24)

        head = ctk.CTkFrame(inner, fg_color="transparent")
        head.pack(fill="x")
        left = ctk.CTkFrame(head, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(left, text="ANPR Recognition", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(anchor="w")
        ctk.CTkLabel(left, text="System Accuracy", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
        
        icon_bg = ctk.CTkFrame(head, fg_color=COLORS["primary_fixed"], corner_radius=16, width=32, height=32)
        icon_bg.pack(side="right")
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text="📷", text_color=COLORS["primary"]).place(relx=0.5, rely=0.5, anchor="center")

        gauge = ctk.CTkFrame(inner, fg_color="transparent")
        gauge.pack(expand=True, fill="both")
        
        canvas = tk.Canvas(gauge, bg=COLORS["surface_container_lowest"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        def draw_gauge(event):
            canvas.delete("all")
            w = event.width
            h = event.height
            if w <= 1 or h <= 1: return
            
            gw = min(w * 0.8, h * 1.5)
            gh = gw / 2
            
            x0 = (w - gw) / 2
            y0 = h - gh - 30
            x1 = x0 + gw
            y1 = y0 + gw
            
            thick = 16
            canvas.create_arc(x0, y0, x1, y1, start=0, extent=180, style=tk.ARC, outline=COLORS["surface_container_high"], width=thick)
            canvas.create_arc(x0, y0, x1, y1, start=180, extent=-177, style=tk.ARC, outline=COLORS["primary"], width=thick)
            
            canvas.create_text(w/2, y0 + gh - 10, text="98.4%", font=("Inter", 36, "bold"), fill=COLORS["on_surface"], anchor="s")
            canvas.create_text(w/2, y0 + gh + 15, text="↗ +0.2% vs last week", font=("Inter", 12, "bold"), fill="#16a34a", anchor="n")
            
        canvas.bind("<Configure>", draw_gauge)

    def _build_yolo(self, parent, row, col, colspan):
        card = ctk.CTkFrame(parent, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12, height=320)
        card.grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=(0, 16))
        card.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=24)

        head = ctk.CTkFrame(inner, fg_color="transparent")
        head.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(head, text="YOLOv11 Confidence", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(side="left")
        
        badge = ctk.CTkFrame(head, fg_color=COLORS["primary_fixed"], corner_radius=4)
        badge.pack(side="right")
        ctk.CTkLabel(badge, text="AI Engine", font=FONTS["label_md"], text_color=COLORS["on_primary_fixed"]).pack(padx=8, pady=2)

        chart = ctk.CTkFrame(inner, fg_color="transparent")
        chart.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(chart, bg=COLORS["surface_container_lowest"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        def draw_yolo(event):
            canvas.delete("all")
            w = event.width
            h = event.height
            if w <= 1 or h <= 1: return
            
            canvas.create_line(0, 0, 0, h, fill=COLORS["outline_variant"])
            canvas.create_line(0, h-1, w, h-1, fill=COLORS["outline_variant"])
            
            import math
            pts = [
                (0.05 * w, 0.8 * h),
                (0.25 * w, 0.2 * h),
                (0.50 * w, 0.6 * h),
                (0.75 * w, 0.1 * h),
                (0.95 * w, 0.4 * h)
            ]
            
            # Generate smooth line points using cosine interpolation
            smooth_pts = []
            for i in range(len(pts) - 1):
                x0, y0 = pts[i]
                x1, y1 = pts[i+1]
                steps = 20
                for s in range(steps):
                    t = s / steps
                    mu2 = (1 - math.cos(t * math.pi)) / 2
                    x = x0 + (x1 - x0) * t
                    y = y0 * (1 - mu2) + y1 * mu2
                    smooth_pts.extend([x, y])
            smooth_pts.extend([pts[-1][0], pts[-1][1]]) # add last point
            
            canvas.create_line(smooth_pts, fill=COLORS["primary"], width=4)
            
            # Draw the dots EXACTLY on the points
            for x, y in pts:
                canvas.create_oval(x-4, y-4, x+4, y+4, fill=COLORS["surface_container_lowest"], outline=COLORS["primary"], width=2)
                
        canvas.bind("<Configure>", draw_yolo)

        avg_box = ctk.CTkFrame(chart, fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=6)
        avg_box.place(relx=1.0, rely=0, anchor="ne", x=-8, y=8)
        ctk.CTkLabel(avg_box, text="0.92", font=("Inter", 16, "bold"), text_color=COLORS["on_surface"]).pack(padx=12, pady=(4, 0))
        ctk.CTkLabel(avg_box, text="Avg Conf", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(padx=12, pady=(0, 4))

    def _build_parking(self, parent, row, col, colspan):
        card = ctk.CTkFrame(parent, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12, height=320)
        card.grid(row=row, column=col, columnspan=colspan, sticky="nsew")
        card.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=24)

        head = ctk.CTkFrame(inner, fg_color="transparent")
        head.pack(fill="x", pady=(0, 24))
        ctk.CTkLabel(head, text="Parking Bay Occupancy", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(side="left")
        
        leg = ctk.CTkFrame(head, fg_color="transparent")
        leg.pack(side="right")
        
        for c, t in [(COLORS["surface_container_high"], "Low"), (COLORS["primary_fixed"], "Med"), (COLORS["primary"], "High")]:
            item = ctk.CTkFrame(leg, fg_color="transparent")
            item.pack(side="left", padx=8)
            dot = ctk.CTkFrame(item, fg_color=c, width=12, height=12, corner_radius=6)
            dot.pack(side="left", padx=(0, 4))
            ctk.CTkLabel(item, text=t, font=FONTS["label_md"], text_color=COLORS["on_surface"]).pack(side="left")

        # Stacked bar chart for 7 days
        days_cont = ctk.CTkFrame(inner, fg_color="transparent")
        days_cont.pack(fill="both", expand=True)
        
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        C_EMP = "transparent"
        C_L = COLORS["surface_container_high"]
        C_M = COLORS["primary_fixed"]
        C_H = COLORS["primary"]

        stacks = [
            [C_L, C_L, C_H, C_H],       # Mon
            [C_EMP, C_L, C_L, C_H],     # Tue
            [C_L, C_L, C_H, C_H],       # Wed
            [C_M, C_H, C_H, C_H],       # Thu
            [C_L, C_L, C_L, C_H],       # Fri
            [C_EMP, C_EMP, C_L, C_L],   # Sat
            [C_EMP, C_EMP, C_EMP, C_L]  # Sun
        ]

        days_cont.grid_rowconfigure(0, weight=1)

        for i, (day, stack) in enumerate(zip(days, stacks)):
            days_cont.grid_columnconfigure(i, weight=1, uniform="day")
            col_frame = ctk.CTkFrame(days_cont, fg_color="transparent")
            col_frame.grid(row=0, column=i, sticky="nsew", padx=2)
            
            bar_area = ctk.CTkFrame(col_frame, fg_color="transparent")
            bar_area.pack(fill="both", expand=True, pady=(0, 4))
            
            for c in stack:
                # Add blocks from top to bottom
                blk = ctk.CTkFrame(bar_area, fg_color=c, corner_radius=4, height=1)
                blk.pack(fill="both", expand=True, pady=2)
            
            font = ("Inter", 12, "bold") if day == "Thu" else FONTS["label_md"]
            col = COLORS["primary"] if day == "Thu" else COLORS["on_surface_variant"]
            ctk.CTkLabel(col_frame, text=day, font=font, text_color=col).pack(side="bottom")
