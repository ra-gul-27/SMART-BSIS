import tkinter as tk
import tkinter.font as tkfont
import customtkinter as ctk
from app.constants import COLORS, FONTS
from app.models.dashboard_model import DashboardModel

class BusTicker(ctk.CTkFrame):
    """
    Electronic LED Bus destination/name board ticker for Event Stream details.
    Continuous seamless horizontal scrolling with auto-pause on mouse hover.
    """
    def __init__(self, master, text, font=None, text_color="#334155", bg_color="transparent", speed=1, **kwargs):
        super().__init__(master, fg_color=bg_color, height=22, **kwargs)
        self.pack_propagate(False)
        self.grid_propagate(False)

        self.raw_text = text
        self.font = font or FONTS["body_md"]
        self.text_color = text_color
        self.speed = speed
        self._timer = None
        self._paused = False

        if isinstance(self.font, tuple):
            self.tk_font = tkfont.Font(family=self.font[0], size=self.font[1], weight=self.font[2] if len(self.font) > 2 else "normal")
        else:
            self.tk_font = tkfont.nametofont("TkDefaultFont")

        self.separator = "     •     "
        self.display_text = f"{self.raw_text}{self.separator}"
        self.text_width = max(self.tk_font.measure(self.display_text), 80)

        canvas_bg = bg_color if bg_color != "transparent" else "#ffffff"
        self.canvas = tk.Canvas(
            self,
            bg=canvas_bg,
            highlightthickness=0,
            bd=0,
            height=20
        )
        self.canvas.pack(fill="both", expand=True)

        self.x1 = 0
        self.x2 = self.text_width
        self.item1 = self.canvas.create_text(self.x1, 10, text=self.display_text, anchor="w", font=self.tk_font, fill=self.text_color)
        self.item2 = self.canvas.create_text(self.x2, 10, text=self.display_text, anchor="w", font=self.tk_font, fill=self.text_color)

        self.canvas.bind("<Enter>", lambda e: self.pause())
        self.canvas.bind("<Leave>", lambda e: self.resume())

        self._animate()

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def _animate(self):
        if not self.winfo_exists():
            return
        try:
            if not self._paused:
                self.x1 -= self.speed
                self.x2 -= self.speed

                if self.x1 <= -self.text_width:
                    self.x1 = self.x2 + self.text_width
                if self.x2 <= -self.text_width:
                    self.x2 = self.x1 + self.text_width

                self.canvas.coords(self.item1, self.x1, 10)
                self.canvas.coords(self.item2, self.x2, 10)

            self._timer = self.after(35, self._animate)
        except Exception:
            pass

    def destroy(self):
        if hasattr(self, "_timer") and self._timer:
            try:
                self.after_cancel(self._timer)
            except Exception:
                pass
        super().destroy()

def add_hover_effect(widget, hover_color, default_color, hover_width=2, default_width=1):
    def on_enter(e):
        widget.configure(border_color=hover_color, border_width=hover_width)
    def on_leave(e):
        try:
            x, y = widget.winfo_pointerxy()
            wx, wy = widget.winfo_rootx(), widget.winfo_rooty()
            ww, wh = widget.winfo_width(), widget.winfo_height()
            if not (wx <= x <= wx + ww and wy <= y <= wy + wh):
                widget.configure(border_color=default_color, border_width=default_width)
        except Exception:
            widget.configure(border_color=default_color, border_width=default_width)
            
    def bind_recursive(w):
        w.bind("<Enter>", on_enter, add="+")
        w.bind("<Leave>", on_leave, add="+")
        for child in w.winfo_children():
            bind_recursive(child)
            
    bind_recursive(widget)

class KPIWidget(ctk.CTkFrame):
    def __init__(self, master, title, value, icon, subtitle=None, is_alert=False, sub_bg=False, **kwargs):
        bg_color = COLORS["error_container"] if is_alert else COLORS["surface_container_lowest"]
        border_color = COLORS["error"] if is_alert else COLORS["primary"]
        super().__init__(master, fg_color=bg_color, border_color=border_color, border_width=2, corner_radius=12, **kwargs)
        
        self.pack_propagate(False)

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=16, pady=(16, 8))

        title_color = COLORS["error"] if is_alert else COLORS["on_surface_variant"]
        icon_color = COLORS["error"] if is_alert else COLORS["primary"] if icon != "P" else COLORS["outline"]
        
        title_lbl = ctk.CTkLabel(
            top_frame, text=title.upper(), font=FONTS["label_md"], text_color=title_color, justify="left"
        )
        title_lbl.pack(side="left", anchor="n")
        
        icon_lbl = ctk.CTkLabel(
            top_frame, text=icon, font=("Arial", 20), text_color=icon_color
        )
        icon_lbl.pack(side="right", anchor="n")

        val_frame = ctk.CTkFrame(self, fg_color="transparent")
        val_frame.pack(fill="x", padx=16, pady=(0, 16))
        
        val_color = COLORS["error"] if is_alert else COLORS["on_surface"]
        self.val_lbl = ctk.CTkLabel(
            val_frame, text=value, font=FONTS["display"], text_color=val_color
        )
        self.val_lbl.pack(side="left", anchor="w")

        if subtitle:
            if sub_bg:
                sub_frame = ctk.CTkFrame(val_frame, fg_color=COLORS["primary_fixed"], corner_radius=16)
                sub_frame.pack(side="left", anchor="sw", padx=8, pady=4)
                sub_lbl = ctk.CTkLabel(
                    sub_frame, text=subtitle, font=("Inter", 11, "bold"), text_color=COLORS["primary"]
                )
                sub_lbl.pack(padx=8, pady=2)
            else:
                sub_lbl = ctk.CTkLabel(
                    val_frame, text=subtitle, font=("Inter", 11), text_color=COLORS["primary"] if not is_alert else COLORS["error"]
                )
                sub_lbl.pack(side="left", anchor="sw", padx=8, pady=6)

    def update_value(self, new_value):
        self.val_lbl.configure(text=str(new_value))

class DashboardView(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller=None, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.app_controller = app_controller
        
        self.grid_columnconfigure(0, weight=1)

        # 1. HEADER
        self._build_header()

        # 2. KPI GRID
        self._build_kpis()

        # 3. MAIN CONTENT (Bento Box style)
        self._build_main_content()

    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 16))
        header_frame.grid_columnconfigure(0, weight=1)

        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(
            title_frame, text="Operational Dashboard", font=FONTS["headline_lg"], text_color=COLORS["on_background"]
        ).pack(anchor="w")
        ctk.CTkLabel(
            title_frame, text="Real-time bus stand overview and monitoring", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]
        ).pack(anchor="w")

        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(
            btn_frame, text="+ Add Bus", fg_color=COLORS["primary"], text_color=COLORS["on_primary"], font=FONTS["body_md"],
            command=lambda: self.app_controller.show_view("BusManagement") if self.app_controller else None
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            btn_frame, text="+ Add Route", fg_color=COLORS["surface_container_low"], border_color=COLORS["primary"], border_width=1, text_color=COLORS["primary"], font=FONTS["body_md"],
            command=lambda: self.app_controller.show_view("RouteManagement") if self.app_controller else None
        ).pack(side="left", padx=4)

    def _build_kpis(self):
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.grid(row=1, column=0, sticky="ew", padx=32, pady=16)
        
        for i in range(6):
            kpi_frame.grid_columnconfigure(i, weight=1, uniform="kpi")

        kpis = DashboardModel.get_kpis()
        self.kpi_widgets = []

        for i, kpi in enumerate(kpis):
            widget = KPIWidget(
                kpi_frame, 
                title=kpi["title"], 
                value=kpi["value"], 
                icon=kpi["icon"],
                subtitle=kpi["sub"], 
                is_alert=kpi["alert"],
                sub_bg=kpi["sub_bg"],
                height=130
            )
            widget.grid(row=0, column=i, sticky="ew", padx=8)
            self.kpi_widgets.append(widget)

    def _build_main_content(self):
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=2, column=0, sticky="nsew", padx=32, pady=16)
        content_frame.grid_columnconfigure(0, weight=2)
        content_frame.grid_columnconfigure(1, weight=1)

        # LEFT COLUMN (Parking & Actions)
        left_col = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        # Parking Bay Status
        parking_frame = ctk.CTkFrame(left_col, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        parking_frame.pack(fill="x", pady=(0, 16))
        
        p_header = ctk.CTkFrame(parking_frame, fg_color=COLORS["surface_container_low"], corner_radius=12, height=48)
        p_header.pack(fill="x")
        ctk.CTkLabel(p_header, text="⊞ Parking Bay Status", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(side="left", padx=16, pady=12)

        legend_frame = ctk.CTkFrame(p_header, fg_color="transparent")
        legend_frame.pack(side="right", padx=16)
        
        ctk.CTkLabel(legend_frame, text="●", text_color=COLORS["outline_variant"], font=("Arial", 16)).pack(side="left")
        ctk.CTkLabel(legend_frame, text="Available", text_color=COLORS["on_surface_variant"], font=("Inter", 12)).pack(side="left", padx=(4, 12))
        
        ctk.CTkLabel(legend_frame, text="●", text_color=COLORS["primary"], font=("Arial", 16)).pack(side="left")
        ctk.CTkLabel(legend_frame, text="Occupied", text_color=COLORS["on_surface_variant"], font=("Inter", 12)).pack(side="left", padx=(4, 0))

        p_grid = ctk.CTkFrame(parking_frame, fg_color=COLORS["surface"])
        p_grid.pack(fill="both", expand=True, padx=16, pady=16)
        
        for i in range(4):
            p_grid.grid_columnconfigure(i, weight=1, uniform="bay")

        bays = DashboardModel.get_parking_bays()

        for i, bay in enumerate(bays):
            row = i // 4
            col = i % 4
            
            is_occ = bay["status"] == "Occupied"
            bg = COLORS["primary"] if is_occ else COLORS["surface_container_lowest"]
            tc = COLORS["on_primary"] if is_occ else COLORS["outline"]
            border = 0 if is_occ else 1
            default_bc = COLORS["outline_variant"] if not is_occ else COLORS["primary"]

            bay_card = ctk.CTkFrame(p_grid, fg_color=bg, border_color=default_bc, border_width=border if border>0 else 1, corner_radius=8, height=80)
            bay_card.pack_propagate(False)
            bay_card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)
            
            # Hover effect for bay cards
            hover_c = COLORS["on_primary_fixed_variant"] if is_occ else COLORS["primary"]
            add_hover_effect(bay_card, hover_color=hover_c, default_color=default_bc, hover_width=2, default_width=border if border>0 else 1)

            if is_occ:
                icon_lbl = ctk.CTkLabel(bay_card, text="ⓘ", text_color=COLORS["on_primary"], font=("Arial", 12))
                icon_lbl.place(relx=0.85, rely=0.15, anchor="center")

            ctk.CTkLabel(bay_card, text=bay["id"], font=FONTS["headline_md"], text_color=tc).pack(pady=(16,0))
            sub_text = bay["vehicle"] if is_occ else "Available"
            sub_tc = COLORS["on_primary"] if is_occ else COLORS["on_surface_variant"]
            ctk.CTkLabel(bay_card, text=sub_text, font=("Inter", 10), text_color=sub_tc).pack()

        # Quick Actions
        actions_grid = ctk.CTkFrame(left_col, fg_color="transparent")
        actions_grid.pack(fill="x")
        
        for i in range(4):
            actions_grid.grid_columnconfigure(i, weight=1, uniform="action")

        actions = [
            ("Configure Bay", "⚙", "ParkingBayManagement"), 
            ("View Cameras", "🎥", "LiveMonitoring1"), 
            ("Generate Report", "📄", "ReportsAnalytics"), 
            ("Terminal Map", "🗺", "Dashboard")
        ]
        for i, (act, icon, view_name) in enumerate(actions):
            act_card = ctk.CTkFrame(actions_grid, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12, height=100)
            act_card.pack_propagate(False)
            act_card.grid(row=0, column=i, sticky="nsew", padx=8)
            
            # Make the whole card clickable by binding a click event
            def route_to_view(e, v=view_name):
                if self.app_controller:
                    self.app_controller.show_view(v)
                    
            act_card.bind("<Button-1>", route_to_view)
            
            add_hover_effect(act_card, hover_color=COLORS["primary"], default_color=COLORS["outline_variant"])
            
            icon_container = ctk.CTkFrame(act_card, fg_color=COLORS["primary"], width=32, height=32, corner_radius=16)
            icon_container.pack_propagate(False)
            icon_container.pack(pady=(16, 4))
            
            lbl1 = ctk.CTkLabel(icon_container, text=icon, font=("Arial", 16), text_color=COLORS["on_primary"])
            lbl1.pack(expand=True)
            lbl1.bind("<Button-1>", route_to_view)
            
            lbl2 = ctk.CTkLabel(act_card, text=act, font=FONTS["body_md"], text_color=COLORS["on_surface"])
            lbl2.pack()
            lbl2.bind("<Button-1>", route_to_view)

        # RIGHT COLUMN (Event Stream)
        right_col = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        events_frame = ctk.CTkFrame(right_col, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        events_frame.pack(fill="both", expand=True)

        e_header = ctk.CTkFrame(events_frame, fg_color=COLORS["surface_container_low"], corner_radius=12, height=48)
        e_header.pack(fill="x")
        ctk.CTkLabel(e_header, text="🕒 Event Stream", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(side="left", padx=16, pady=12)

        dot_frame = ctk.CTkFrame(e_header, fg_color="transparent")
        dot_frame.pack(side="right", padx=16)
        
        outer_dot = ctk.CTkFrame(dot_frame, fg_color=COLORS["primary_fixed"], width=16, height=16, corner_radius=8)
        outer_dot.pack_propagate(False)
        outer_dot.pack()
        inner_dot = ctk.CTkFrame(outer_dot, fg_color=COLORS["primary"], width=8, height=8, corner_radius=4)
        inner_dot.place(relx=0.5, rely=0.5, anchor="center")

        self.e_list = ctk.CTkFrame(events_frame, fg_color=COLORS["surface"])
        self.e_list.pack(fill="both", expand=True, padx=16, pady=16)

        events = DashboardModel.get_events()

        for time, title, desc, color, is_alert in events:
            bg_color = COLORS["error_container"] if is_alert else "transparent"
            item_frame = ctk.CTkFrame(self.e_list, fg_color=bg_color, corner_radius=6)
            item_frame.pack(fill="x", pady=4, padx=4)
            
            content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            content_frame.pack(fill="x", padx=8, pady=8)
            
            ctk.CTkLabel(content_frame, text=time, font=FONTS["data_mono"], text_color=COLORS["outline"], width=60, anchor="w").pack(side="left", anchor="n")
            
            text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True, padx=8)
            
            ctk.CTkLabel(text_frame, text=title, font=FONTS["label_md"], text_color=color).pack(anchor="w")
            
            # Electronic LED Bus Name Board marquee scrolling ticker for details alone
            ticker_bg = COLORS["error_container"] if is_alert else COLORS["surface"]
            ticker_fg = COLORS["error"] if is_alert else COLORS["on_surface_variant"]
            ticker = BusTicker(text_frame, text=desc, font=FONTS["body_md"], text_color=ticker_fg, bg_color=ticker_bg, speed=1)
            ticker.pack(fill="x", expand=True, pady=(2, 0))
            
            if not is_alert and time != events[-1][0]:
                line = ctk.CTkFrame(self.e_list, fg_color=COLORS["outline_variant"], height=1)
                line.pack(fill="x", padx=12, pady=(0, 4))


