import customtkinter as ctk
from app.constants import COLORS, FONTS
from app.models.schedule_model import ScheduleModel

class ScheduleAndTimingsView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.app_controller = app_controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) 

        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.grid(row=0, column=0, sticky="nsew")
        self.scroll_container.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_tabs()
        
        self.content_grid = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.content_grid.grid(row=2, column=0, sticky="nsew", padx=32, pady=16)
        
        # 3:1 ratio for Table : Side Panel
        self.content_grid.grid_columnconfigure(0, weight=3, uniform="col_main")
        self.content_grid.grid_columnconfigure(1, weight=1, uniform="col_main")
        
        self._build_table(self.content_grid)
        self._build_side_panel(self.content_grid)

    def _build_header(self):
        header = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 16))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left, text="Schedule & Timings", font=FONTS["headline_lg"], text_color=COLORS["on_surface"]).pack(anchor="w")
        ctk.CTkLabel(left, text="Manage bus departures, arrivals and terminal schedules", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")

        # Date Selector
        date_sel = ctk.CTkFrame(right, fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=8)
        date_sel.pack(side="left", padx=(0, 16))
        
        ctk.CTkButton(date_sel, text="<", width=32, height=32, fg_color="transparent", text_color=COLORS["on_surface_variant"], hover_color=COLORS["surface_container"]).pack(side="left", padx=4)
        ctk.CTkLabel(date_sel, text="📅 Oct 24, 2023", font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(side="left", padx=8)
        ctk.CTkButton(date_sel, text=">", width=32, height=32, fg_color="transparent", text_color=COLORS["on_surface_variant"], hover_color=COLORS["surface_container"]).pack(side="left", padx=4)

        ctk.CTkButton(
            right, text="+ Add Schedule", font=FONTS["label_md"], 
            fg_color=COLORS["primary"], text_color=COLORS["on_primary"], hover_color=COLORS["primary_container"]
        ).pack(side="left")

    def _build_tabs(self):
        tab_container = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        tab_container.grid(row=1, column=0, sticky="ew", padx=32)
        
        # We need a bottom border for the whole tab row
        bottom_border = ctk.CTkFrame(tab_container, fg_color=COLORS["outline_variant"], height=1)
        bottom_border.place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        tab1 = ctk.CTkFrame(tab_container, fg_color="transparent")
        tab1.pack(side="left", padx=(0, 16))
        ctk.CTkLabel(tab1, text="☰ TABLE VIEW", font=("Inter", 12, "bold"), text_color=COLORS["primary"]).pack(pady=(8, 12), padx=8)
        # Active tab indicator
        indicator = ctk.CTkFrame(tab1, fg_color=COLORS["primary"], height=2)
        indicator.place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        tab2 = ctk.CTkFrame(tab_container, fg_color="transparent")
        tab2.pack(side="left", padx=16)
        ctk.CTkLabel(tab2, text="∿ TIMELINE VIEW", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(pady=(8, 12), padx=8)


    def _build_table(self, parent):
        table_card = ctk.CTkFrame(parent, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        table_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        table_card.grid_columnconfigure(0, weight=1)
        
        # Filters Header
        filter_row = ctk.CTkFrame(table_card, fg_color=COLORS["surface_container_lowest"], corner_radius=12)
        filter_row.pack(fill="x", padx=1, pady=1)
        filter_content = ctk.CTkFrame(filter_row, fg_color="transparent")
        filter_content.pack(fill="x", padx=16, pady=12)
        
        left_filters = ctk.CTkFrame(filter_content, fg_color="transparent")
        left_filters.pack(side="left")
        
        ctk.CTkEntry(left_filters, placeholder_text="All Routes", font=FONTS["body_md"], fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], text_color=COLORS["on_surface"], width=140, height=32).pack(side="left", padx=(0, 8))
        ctk.CTkEntry(left_filters, placeholder_text="All Bays", font=FONTS["body_md"], fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], text_color=COLORS["on_surface"], width=140, height=32).pack(side="left")
        
        legend = ctk.CTkFrame(filter_content, fg_color="transparent")
        legend.pack(side="right")
        
        ctk.CTkLabel(legend, text="●", text_color="#3B82F6", font=("Arial", 14)).pack(side="left", padx=(0, 4))
        ctk.CTkLabel(legend, text="Scheduled", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(side="left", padx=(0, 12))
        
        ctk.CTkLabel(legend, text="●", text_color="#10B981", font=("Arial", 14)).pack(side="left", padx=(0, 4))
        ctk.CTkLabel(legend, text="Boarding", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(side="left", padx=(0, 12))
        
        ctk.CTkLabel(legend, text="●", text_color="#EF4444", font=("Arial", 14)).pack(side="left", padx=(0, 4))
        ctk.CTkLabel(legend, text="Delayed", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(side="left")

        # Header Row
        border1 = ctk.CTkFrame(table_card, fg_color=COLORS["outline_variant"], height=1)
        border1.pack(fill="x", padx=1)
        
        thead = ctk.CTkFrame(table_card, fg_color=COLORS["surface_container_low"], corner_radius=0)
        thead.pack(fill="x", padx=1)
        th_row = ctk.CTkFrame(thead, fg_color="transparent")
        th_row.pack(fill="x", padx=16, pady=8)

        self.cols = [
            ("BUS NO.", 1.2), ("ROUTE / DESTINATION", 2), ("BAY", 0.8), 
            ("DEPARTURE", 1.2), ("EST. ARRIVAL", 1.2), ("FARE", 0.8), ("STATUS", 1.5), ("ACTIONS", 1)
        ]
        
        for i, (c, w) in enumerate(self.cols):
            th_row.grid_columnconfigure(i, weight=int(w*10), uniform="col")
            anchor = "w" if i < len(self.cols) - 1 else "e"
            sticky = "w" if anchor == "w" else "e"
            th = ctk.CTkLabel(th_row, text=c, font=FONTS["label_md"], text_color=COLORS["on_surface_variant"])
            th.grid(row=0, column=i, sticky=sticky, padx=4)

        border2 = ctk.CTkFrame(table_card, fg_color=COLORS["outline_variant"], height=1)
        border2.pack(fill="x", padx=1)

        # Table Body Container
        self.grid_container = ctk.CTkFrame(table_card, fg_color="transparent")
        self.grid_container.pack(fill="x")
        self.table_card = table_card

        self._populate_grid()

        # Pagination Footer
        border_footer = ctk.CTkFrame(table_card, fg_color=COLORS["outline_variant"], height=1)
        border_footer.pack(fill="x", padx=1)
        
        tfoot = ctk.CTkFrame(table_card, fg_color=COLORS["surface_container_lowest"], corner_radius=12)
        tfoot.pack(fill="x", padx=1, pady=(0, 1))
        tfoot_mask = ctk.CTkFrame(tfoot, fg_color=COLORS["surface_container_lowest"], height=8, corner_radius=0)
        tfoot_mask.pack(side="top", fill="x")

        tfoot_content = ctk.CTkFrame(tfoot, fg_color="transparent")
        tfoot_content.pack(fill="x", padx=16, pady=(4, 12))

        ctk.CTkLabel(tfoot_content, text="Showing 1 to 10 of 124 schedules", font=("Inter", 12), text_color=COLORS["on_surface_variant"]).pack(side="left")
        
        pag_wrapper = ctk.CTkFrame(tfoot_content, fg_color="transparent")
        pag_wrapper.pack(side="right")
        
        for p in ["Prev", "1", "2", "3", "Next"]:
            is_active = (p == "1")
            fg = COLORS["primary"] if is_active else "transparent"
            tc = COLORS["on_primary"] if is_active else COLORS["on_surface_variant"]
            border = 0 if is_active else 1
            ctk.CTkButton(
                pag_wrapper, text=p, width=32, height=28, font=("Inter", 12), 
                fg_color=fg, text_color=tc, border_color=COLORS["outline_variant"], border_width=border,
                hover_color=COLORS["surface_container"]
            ).pack(side="left", padx=2)

    def _populate_grid(self):
        for widget in self.grid_container.winfo_children():
            widget.destroy()

        schedules = ScheduleModel.get_all_schedules()

        for i, row in enumerate(schedules):
            # Parse Status for styles
            status = row["status"].upper()
            if "DELAYED" in status:
                s_bg = "#fee2e2"
                s_fg = COLORS["error"]
                s_b = "#fecaca"
                strike = True
            elif "BOARDING" in status:
                s_bg = "#d1fae5"
                s_fg = "#059669"
                s_b = "#a7f3d0"
                strike = False
            elif "DEPARTED" in status:
                s_bg = COLORS["surface_container"]
                s_fg = COLORS["outline"]
                s_b = COLORS["outline_variant"]
                strike = False
            else:
                s_bg = "#e0e7ff"
                s_fg = COLORS["primary"]
                s_b = "#c7d2fe"
                strike = False

            bg_color = "transparent" if i % 2 == 0 else COLORS["surface_container_low"]
            
            tr = ctk.CTkFrame(self.grid_container, fg_color=bg_color, corner_radius=0)
            tr.pack(fill="x", padx=1)
            
            tr_content = ctk.CTkFrame(tr, fg_color="transparent")
            tr_content.pack(fill="x", padx=16, pady=12)
            
            for j, (c, w) in enumerate(self.cols):
                tr_content.grid_columnconfigure(j, weight=int(w*10), uniform="col")

            # Col 1: Bus No
            c1 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c1.grid(row=0, column=0, sticky="ew", padx=4)
            ctk.CTkLabel(c1, text=row["bus"], font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(anchor="w")

            # Col 2: Route & Dest
            c2 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c2.grid(row=0, column=1, sticky="ew", padx=4)
            ctk.CTkLabel(c2, text=row["route"], font=("Inter", 14, "bold"), text_color=COLORS["on_surface"]).pack(anchor="w")
            ctk.CTkLabel(c2, text=row["dest"], font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")

            # Col 3: Bay
            c3 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c3.grid(row=0, column=2, sticky="ew", padx=4)
            ctk.CTkLabel(c3, text=row["bay"], font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(anchor="w")

            # Col 4: Departure
            c4 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c4.grid(row=0, column=3, sticky="ew", padx=4)
            overstruck = bool(strike)
            ctk.CTkLabel(c4, text=row["dep"], font=("Inter", 14, "overstrike" if overstruck else "normal"), text_color=COLORS["on_surface_variant"] if overstruck else COLORS["on_surface"]).pack(anchor="w")

            # Col 5: Est Arrival
            c5 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c5.grid(row=0, column=4, sticky="ew", padx=4)
            ctk.CTkLabel(c5, text=row["arr"], font=("Inter", 14), text_color=COLORS["on_surface"]).pack(anchor="w")

            # Col 6: Fare
            c6 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c6.grid(row=0, column=5, sticky="ew", padx=4)
            ctk.CTkLabel(c6, text=row["fare"], font=("Inter", 14), text_color=COLORS["on_surface"]).pack(anchor="w")

            # Col 7: Status
            c7 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c7.grid(row=0, column=6, sticky="ew", padx=4)
            s_badge = ctk.CTkFrame(c7, fg_color=s_bg, border_color=s_b, border_width=1, corner_radius=12)
            s_badge.pack(anchor="w")
            ctk.CTkLabel(s_badge, text=status, text_color=s_fg, font=("Inter", 10, "bold")).pack(padx=8, pady=2)

            # Col 8: Actions
            c8 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c8.grid(row=0, column=7, sticky="ew", padx=4)
            c8_wrapper = ctk.CTkFrame(c8, fg_color="transparent")
            c8_wrapper.pack(anchor="e")
            ctk.CTkButton(c8_wrapper, text="⋮", width=32, height=32, fg_color="transparent", text_color=COLORS["on_surface_variant"], hover_color=COLORS["surface_container"]).pack(side="left")

            if i < len(schedules) - 1:
                border = ctk.CTkFrame(self.grid_container, fg_color=COLORS["outline_variant"], height=1)
                border.pack(fill="x", padx=1)

    def _build_side_panel(self, parent):
        side_panel = ctk.CTkFrame(parent, fg_color="transparent")
        side_panel.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        
        # Bay Status Card
        bay_card = ctk.CTkFrame(side_panel, fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        bay_card.pack(fill="x", pady=(0, 24))
        
        b_inner = ctk.CTkFrame(bay_card, fg_color="transparent")
        b_inner.pack(fill="x", padx=16, pady=16)
        
        ctk.CTkLabel(b_inner, text="🅿 Bay Status", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(anchor="w")
        ctk.CTkLabel(b_inner, text="Current allocation & availability", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(0, 16))

        bays = [
            {"id": "A1", "bus": "NY-102 (Boarding)", "desc": "Exp. Central • Dep: 08:15", "type": "boarding", "c_bg": "#f0fdf4", "c_fg": "#10b981", "icon": "✓"},
            {"id": "A2", "bus": "Available", "desc": "Next: 09:00 AM", "type": "available", "c_bg": "transparent", "c_fg": COLORS["outline_variant"], "icon": "○"},
            {"id": "A4", "bus": "CH-882 (Delayed)", "desc": "Intercity • Dep: 08:00", "type": "delayed", "c_bg": "#fef2f2", "c_fg": COLORS["error"], "icon": "⚠"}
        ]

        for bay in bays:
            item = ctk.CTkFrame(b_inner, fg_color=bay["c_bg"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=8)
            item.pack(fill="x", pady=4)
            
            i_content = ctk.CTkFrame(item, fg_color="transparent")
            i_content.pack(fill="x", padx=8, pady=8)
            
            if bay["type"] != "available":
                indicator = ctk.CTkFrame(item, fg_color=bay["c_fg"], width=4)
                indicator.place(relx=0, rely=0, relheight=1.0, anchor="nw")

            # Bay ID box
            box = ctk.CTkFrame(i_content, fg_color=COLORS["surface_container"], border_color=COLORS["outline_variant"], border_width=1, width=32, height=32, corner_radius=4)
            box.pack(side="left", padx=(8 if bay["type"] != "available" else 0, 8))
            box.pack_propagate(False)
            ctk.CTkLabel(box, text=bay["id"], font=("Inter", 12, "bold"), text_color=COLORS["on_surface"]).place(relx=0.5, rely=0.5, anchor="center")
            
            text_col = ctk.CTkFrame(i_content, fg_color="transparent")
            text_col.pack(side="left")
            ctk.CTkLabel(text_col, text=bay["bus"], font=("Inter", 12, "bold"), text_color=COLORS["on_surface"] if bay["type"] != "available" else COLORS["on_surface_variant"]).pack(anchor="w")
            ctk.CTkLabel(text_col, text=bay["desc"], font=("Inter", 10), text_color=COLORS["on_surface_variant"]).pack(anchor="w")

            ctk.CTkLabel(i_content, text=bay["icon"], font=("Arial", 16), text_color=bay["c_fg"]).pack(side="right", padx=8)

        # System Alerts Card
        alert_card = ctk.CTkFrame(side_panel, fg_color=COLORS["surface"], border_color="#fecaca", border_width=1, corner_radius=12)
        alert_card.pack(fill="x")
        
        a_inner = ctk.CTkFrame(alert_card, fg_color="transparent")
        a_inner.pack(fill="x", padx=16, pady=16)
        
        ctk.CTkLabel(a_inner, text="⚠ System Alerts", font=FONTS["headline_md"], text_color=COLORS["error"]).pack(anchor="w")
        
        msg = ctk.CTkLabel(a_inner, text="Route CH-882 is experiencing a 15-minute delay due to traffic congestion on Highway 4.", font=FONTS["body_md"], text_color=COLORS["on_surface"], wraplength=200, justify="left")
        msg.pack(anchor="w", pady=(8, 16))
        
        ctk.CTkButton(a_inner, text="Acknowledge & Notify Passengers", font=("Inter", 12, "bold"), text_color=COLORS["error"], fg_color="transparent", hover_color="#fee2e2", anchor="w").pack(anchor="w", fill="x")
