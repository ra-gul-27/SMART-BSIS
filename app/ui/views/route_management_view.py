import customtkinter as ctk
from app.constants import COLORS, FONTS
from app.models.route_model import RouteModel

class RouteManagementView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.app_controller = app_controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) 

        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.grid(row=0, column=0, sticky="nsew")
        self.scroll_container.grid_columnconfigure(0, weight=1)

        self._build_header()
        
        self.content_grid = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.content_grid.grid(row=1, column=0, sticky="nsew", padx=32, pady=16)
        # 2:1 ratio for Table : Side Panel
        self.content_grid.grid_columnconfigure(0, weight=2, uniform="col_main")
        self.content_grid.grid_columnconfigure(1, weight=1, uniform="col_main")
        
        self._build_table(self.content_grid)
        self._build_side_panel(self.content_grid)
        self._build_drawer()

    def _build_header(self):
        header = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 16))
        header.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left, text="Route Management", font=FONTS["headline_lg"], text_color=COLORS["on_surface"]).pack(anchor="w")
        ctk.CTkLabel(left, text="Manage bus routes and terminal destinations", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(
            right, text="+ Add Route", font=FONTS["label_md"], 
            fg_color=COLORS["primary"], text_color=COLORS["on_primary"], hover_color=COLORS["primary_container"],
            command=self.open_drawer
        ).pack(side="left")

    def open_drawer(self):
        self.drawer_overlay.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")

    def close_drawer(self):
        self.drawer_overlay.place_forget()

    def _build_table(self, parent):
        table_card = ctk.CTkFrame(parent, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        table_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        table_card.grid_columnconfigure(0, weight=1)
        
        # Table Title Header
        title_row = ctk.CTkFrame(table_card, fg_color=COLORS["surface_container_lowest"], corner_radius=12)
        title_row.pack(fill="x", padx=1, pady=1)
        title_content = ctk.CTkFrame(title_row, fg_color="transparent")
        title_content.pack(fill="x", padx=16, pady=12)
        
        ctk.CTkLabel(title_content, text="⛖ Active Routes", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(side="left")
        self.search_var = ctk.StringVar(value="")
        self.search_entry = ctk.CTkEntry(title_content, placeholder_text="Search routes...", textvariable=self.search_var, font=FONTS["body_md"], fg_color="transparent", border_color=COLORS["outline_variant"], text_color=COLORS["on_surface"], width=200, height=32)
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", lambda e: self._populate_grid())
        
        # Header Row
        border1 = ctk.CTkFrame(table_card, fg_color=COLORS["outline_variant"], height=1)
        border1.pack(fill="x", padx=1)
        
        thead = ctk.CTkFrame(table_card, fg_color=COLORS["surface_container_low"], corner_radius=0)
        thead.pack(fill="x", padx=1)
        th_row = ctk.CTkFrame(thead, fg_color="transparent")
        th_row.pack(fill="x", padx=16, pady=12)

        self.cols = [
            ("Route ID", 1), ("Route Name", 2.5), ("Details", 3), 
            ("Assigned", 1), ("Status", 1.2), ("Actions", 1)
        ]
        
        for i, (c, w) in enumerate(self.cols):
            th_row.grid_columnconfigure(i, weight=int(w*10), uniform="col")
            if c == "Assigned" or c == "Status":
                anchor = "center"
            else:
                anchor = "w" if i < len(self.cols) - 1 else "e"
            
            sticky = "ew" if anchor == "center" else ("w" if anchor == "w" else "e")
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
        ctk.CTkLabel(tfoot_content, text="Showing 1 to 10 of 28 entries", font=("Inter", 12), text_color=COLORS["on_surface_variant"]).pack(side="left")
        
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

        routes = RouteModel.get_all_routes()
        s_query = self.search_var.get().strip().lower() if hasattr(self, "search_var") else ""
        if s_query:
            routes = [r for r in routes if s_query in r["id"].lower() or s_query in r["name"].lower() or s_query in r["desc"].lower()]

        for i, row in enumerate(routes):
            # Alternate row background
            bg_color = "transparent" if i % 2 == 0 else COLORS["surface_container_lowest"]
            
            tr = ctk.CTkFrame(self.grid_container, fg_color=bg_color, corner_radius=0)
            tr.pack(fill="x", padx=1)
            if i < len(routes) - 1:
                border = ctk.CTkFrame(self.grid_container, fg_color=COLORS["outline_variant"], height=1)
                border.pack(fill="x", padx=1)

            tr_content = ctk.CTkFrame(tr, fg_color="transparent")
            tr_content.pack(fill="x", padx=16, pady=16)
            
            for j, (c, w) in enumerate(self.cols):
                tr_content.grid_columnconfigure(j, weight=int(w*10), uniform="col")

            # Col 1: Route ID
            c1 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c1.grid(row=0, column=0, sticky="ew", padx=4)
            ctk.CTkLabel(c1, text=row["route_id"], font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(anchor="w")

            # Col 2: Route Name
            c2 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c2.grid(row=0, column=1, sticky="ew", padx=4)
            name = f"{row['source']} – {row['destination']}"
            ctk.CTkLabel(c2, text=name, font=("Inter", 14, "bold"), text_color=COLORS["on_surface"]).pack(anchor="w")
            if row["source"] and row["destination"]:
                sub = ctk.CTkFrame(c2, fg_color="transparent")
                sub.pack(anchor="w")
                ctk.CTkLabel(sub, text=row["source"], font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(side="left")
                ctk.CTkLabel(sub, text=" ➝ ", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(side="left")
                ctk.CTkLabel(sub, text=row["destination"], font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(side="left")

            # Col 3: Details
            c3 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c3.grid(row=0, column=2, sticky="ew", padx=4)
            d_wrapper = ctk.CTkFrame(c3, fg_color="transparent")
            d_wrapper.pack(anchor="w")
            # Calculate stops from via_stops string (number of commas + 1)
            num_stops = len(str(row['via_stops']).split(',')) if row['via_stops'] else 0
            ctk.CTkLabel(d_wrapper, text=f"📍 {num_stops} Stops", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(side="left", padx=(0, 12))
            ctk.CTkLabel(d_wrapper, text=f"⏱ {row['duration']}", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(side="left", padx=(0, 12))
            ctk.CTkLabel(d_wrapper, text=f"🛣 {row['distance']}", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(side="left")

            # Col 4: Assigned
            c4 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c4.grid(row=0, column=3, sticky="ew", padx=4)
            assigned_dummy = "12" if row["status"] == "Active" else "0"
            ctk.CTkLabel(c4, text=assigned_dummy, font=("Inter", 14, "bold"), text_color=COLORS["primary"]).pack(anchor="center")
            ctk.CTkLabel(c4, text="buses", font=("Inter", 11), text_color=COLORS["on_surface_variant"]).pack(anchor="center")

            # Col 5: Status
            c5 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c5.grid(row=0, column=4, sticky="ew", padx=4)
            s_bg = COLORS["surface_container"] if row["status"] == "Active" else COLORS["error_container"]
            s_fg = COLORS["primary"] if row["status"] == "Active" else COLORS["error"]
            s_badge = ctk.CTkFrame(c5, fg_color=s_bg, corner_radius=6)
            s_badge.pack(anchor="center")
            ctk.CTkLabel(s_badge, text=row["status"].upper(), text_color=s_fg, font=("Inter", 11, "bold")).pack(padx=12, pady=4)

            # Col 6: Actions
            c6 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c6.grid(row=0, column=5, sticky="ew", padx=4)
            c6_wrapper = ctk.CTkFrame(c6, fg_color="transparent")
            c6_wrapper.pack(anchor="e")
            ctk.CTkButton(
                c6_wrapper, text="⚙", width=32, height=32, 
                fg_color="transparent", text_color=COLORS["on_surface_variant"], hover_color=COLORS["surface_container"],
                command=lambda r=row: self._select_route(r)
            ).pack(side="left", padx=4)
            ctk.CTkButton(
                c6_wrapper, text="⏻", width=32, height=32, 
                fg_color="#fee2e2", text_color="#dc2626", hover_color="#fca5a5", corner_radius=6,
                command=lambda rid=row["route_id"]: self._toggle_route(rid)
            ).pack(side="left")

    def _select_route(self, route_data):
        self.selected_route = route_data
        self._build_side_panel(self.content_grid)

    def _toggle_route(self, route_id):
        RouteModel.toggle_route_status(route_id)
        self._populate_grid()
        self._build_side_panel(self.content_grid)

    def _build_side_panel(self, parent):
        if hasattr(self, "side_panel_widget") and self.side_panel_widget:
            self.side_panel_widget.destroy()

        routes = RouteModel.get_all_routes()
        curr_route = getattr(self, "selected_route", None)
        if not curr_route and routes:
            curr_route = routes[0]
        if not curr_route:
            curr_route = {"route_id": "R-01", "source": "Chennai Central", "destination": "Bangalore Shantinagar", "distance": "350 km", "duration": "360 mins", "status": "Active", "via_stops": "Vellore, Ambur, Hosur"}

        side_panel = ctk.CTkFrame(parent, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        side_panel.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        self.side_panel_widget = side_panel
        
        # Content padding
        inner = ctk.CTkFrame(side_panel, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        h_row = ctk.CTkFrame(inner, fg_color="transparent")
        h_row.pack(fill="x", pady=(0, 16))
        
        left_h = ctk.CTkFrame(h_row, fg_color="transparent")
        left_h.pack(side="left")
        ctk.CTkLabel(left_h, text="ROUTE PREVIEW", font=FONTS["label_md"], text_color=COLORS["primary"]).pack(anchor="w")
        ctk.CTkLabel(left_h, text=f"{curr_route['source']} – {curr_route['destination']}", font=("Inter", 15, "bold"), text_color=COLORS["on_surface"]).pack(anchor="w")
        ctk.CTkLabel(left_h, text=f"ID: {curr_route['route_id']}", font=FONTS["data_mono"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
        
        is_active = (curr_route["status"] == "Active")
        badge = ctk.CTkFrame(h_row, fg_color="#ecfdf5" if is_active else "#fee2e2", border_color="#a7f3d0" if is_active else "#fca5a5", border_width=1, corner_radius=12)
        badge.pack(side="right", anchor="n")
        ctk.CTkLabel(badge, text=curr_route["status"].upper(), text_color="#047857" if is_active else "#dc2626", font=("Inter", 10, "bold")).pack(padx=10, pady=2)

        # Mini Stats
        stats = ctk.CTkFrame(inner, fg_color="transparent")
        stats.pack(fill="x", pady=24)
        stats.grid_columnconfigure(0, weight=1)
        stats.grid_columnconfigure(1, weight=1)
        
        s1 = ctk.CTkFrame(stats, fg_color="transparent", border_color=COLORS["outline_variant"], border_width=1, corner_radius=8)
        s1.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(s1, text="Total Distance", font=("Inter", 11), text_color=COLORS["on_surface_variant"]).pack(anchor="w", padx=12, pady=(8,0))
        ctk.CTkLabel(s1, text=str(curr_route.get("distance", "350 km")), font=("Inter", 14, "bold"), text_color=COLORS["on_surface"]).pack(anchor="w", padx=12, pady=(0,8))

        s2 = ctk.CTkFrame(stats, fg_color="transparent", border_color=COLORS["outline_variant"], border_width=1, corner_radius=8)
        s2.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(s2, text="Est. Duration", font=("Inter", 11), text_color=COLORS["on_surface_variant"]).pack(anchor="w", padx=12, pady=(8,0))
        ctk.CTkLabel(s2, text=str(curr_route.get("duration", "360 mins")), font=("Inter", 14, "bold"), text_color=COLORS["on_surface"]).pack(anchor="w", padx=12, pady=(0,8))

        # Timeline Header
        via_text = curr_route.get("via_stops", "Direct Express")
        stops_list = [curr_route["source"]] + [s.strip() for s in via_text.split(",") if s.strip()] + [curr_route["destination"]]
        
        ctk.CTkLabel(inner, text=f"ROUTE STOPS ({len(stops_list)})", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(0, 16))
        
        # Timeline
        tl = ctk.CTkFrame(inner, fg_color="transparent")
        tl.pack(fill="both", expand=True)

        for i, sname in enumerate(stops_list):
            is_endpoint = (i == 0 or i == len(stops_list) - 1)
            item = ctk.CTkFrame(tl, fg_color="transparent")
            item.pack(fill="x", pady=2)
        
        stops = [
            ("Chennai (CMBT)", "Source Terminal • 0 km", True),
            ("Vellore", "ETA: +2h 15m • 140 km", False),
            ("Krishnagiri", "ETA: +4h 00m • 255 km", False),
            ("Salem", "ETA: +5h 30m • 345 km", False),
            ("+ 4 minor stops...", "", "dashed"),
            ("Coimbatore (Gandhipuram)", "Destination • 510 km", True)
        ]
        
        for i, (name, desc, is_main) in enumerate(stops):
            item = ctk.CTkFrame(tl, fg_color="transparent")
            item.pack(fill="x")
            
            gfx = ctk.CTkFrame(item, fg_color="transparent", width=32)
            gfx.pack(side="left", fill="y", padx=(0, 12))
            gfx.pack_propagate(False)
            
            if i > 0:
                top = ctk.CTkFrame(gfx, fg_color=COLORS["outline_variant"], width=2, height=20)
                top.place(relx=0.5, y=0, anchor="n")
                
            if i < len(stops) - 1:
                btm = ctk.CTkFrame(gfx, fg_color=COLORS["outline_variant"], width=2)
                btm.place(relx=0.5, y=20, relheight=1.0, anchor="n")
                if is_main == "dashed":
                    btm.configure(fg_color="transparent") 
                    # Fake dashed line by just using a solid one for now or multiple dots
                    pass
            
            if is_main == True:
                if i == 0:
                    dot = ctk.CTkFrame(gfx, fg_color=COLORS["surface"], border_color=COLORS["primary"], border_width=3, width=16, height=16, corner_radius=8)
                else:
                    dot = ctk.CTkFrame(gfx, fg_color=COLORS["surface"], border_color=COLORS["tertiary_container"], border_width=3, width=16, height=16, corner_radius=8)
                dot.place(relx=0.5, y=20, anchor="center")
            elif is_main == False:
                dot = ctk.CTkFrame(gfx, fg_color=COLORS["outline_variant"], width=8, height=8, corner_radius=4)
                dot.place(relx=0.5, y=20, anchor="center")
            
            content = ctk.CTkFrame(item, fg_color="transparent")
            content.pack(side="left", fill="x", expand=True, pady=10)
            
            if is_main == "dashed":
                ctk.CTkLabel(content, text=name, font=("Inter", 12, "italic"), text_color=COLORS["on_surface_variant"]).pack(anchor="w")
            else:
                ctk.CTkLabel(content, text=name, font=("Inter", 14, "bold" if is_main else "normal"), text_color=COLORS["on_surface"]).pack(anchor="w")
                if desc:
                    ctk.CTkLabel(content, text=desc, font=("Inter", 11), text_color=COLORS["on_surface_variant"]).pack(anchor="w")

        # Footer Buttons
        f_row = ctk.CTkFrame(inner, fg_color="transparent")
        f_row.pack(fill="x", pady=(24, 0))
        f_row.grid_columnconfigure(0, weight=1)
        f_row.grid_columnconfigure(1, weight=1)
        
        ctk.CTkButton(f_row, text="Edit Route", font=FONTS["label_md"], fg_color="transparent", border_color=COLORS["primary"], border_width=1, text_color=COLORS["primary"], hover_color=COLORS["surface_container"]).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(f_row, text="Assign Bus", font=FONTS["label_md"], fg_color=COLORS["primary"], text_color=COLORS["on_primary"], hover_color=COLORS["primary_container"]).grid(row=0, column=1, sticky="ew", padx=(6, 0))

    def _build_drawer(self):
        self.drawer_overlay = ctk.CTkFrame(self, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=0, width=400)
        self.drawer_overlay.pack_propagate(False)

        d_header = ctk.CTkFrame(self.drawer_overlay, fg_color=COLORS["surface_bright"], corner_radius=0, height=64)
        d_header.pack(fill="x")
        d_header.pack_propagate(False)
        
        ctk.CTkLabel(d_header, text="Add New Route", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(side="left", padx=24, pady=16)
        close_btn = ctk.CTkButton(d_header, text="✕", width=32, height=32, fg_color="transparent", text_color=COLORS["on_surface_variant"], hover_color=COLORS["surface_container"], command=self.close_drawer)
        close_btn.pack(side="right", padx=16, pady=16)

        d_border = ctk.CTkFrame(self.drawer_overlay, fg_color=COLORS["outline_variant"], height=1)
        d_border.pack(fill="x")

        d_form = ctk.CTkScrollableFrame(self.drawer_overlay, fg_color="transparent", corner_radius=0)
        d_form.pack(fill="both", expand=True, padx=24, pady=16)

        self.entry_id = self._add_form_field(d_form, "Route ID *", "e.g., R09")
        self.entry_src = self._add_form_field(d_form, "Source City *", "e.g., Chennai")
        self.entry_dst = self._add_form_field(d_form, "Destination City *", "e.g., Madurai")
        
        ctk.CTkLabel(d_form, text="ROUTE DETAILS", font=("Inter", 11, "bold"), text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(24, 8))
        self.entry_stops = self._add_form_field(d_form, "Via Stops (comma separated)", "e.g., Vellore, Salem")
        self.entry_dist = self._add_form_field(d_form, "Distance (km)", "e.g., 510")
        self.entry_dur = self._add_form_field(d_form, "Duration (mins)", "e.g., 450")
        self.entry_status = self._add_form_field(d_form, "Status", "Active", is_dropdown=True)

        d_footer_border = ctk.CTkFrame(self.drawer_overlay, fg_color=COLORS["outline_variant"], height=1)
        d_footer_border.pack(fill="x")
        
        d_footer = ctk.CTkFrame(self.drawer_overlay, fg_color=COLORS["surface_bright"], corner_radius=0, height=72)
        d_footer.pack(fill="x")
        d_footer.pack_propagate(False)

        btn_wrapper = ctk.CTkFrame(d_footer, fg_color="transparent")
        btn_wrapper.pack(side="right", padx=24, pady=16)

        ctk.CTkButton(btn_wrapper, text="Cancel", font=FONTS["label_md"], fg_color="transparent", text_color=COLORS["on_surface"], border_color=COLORS["outline_variant"], border_width=1, hover_color=COLORS["surface_container"], command=self.close_drawer).pack(side="left", padx=8)
        ctk.CTkButton(btn_wrapper, text="Save Route", font=FONTS["label_md"], fg_color=COLORS["primary"], text_color=COLORS["on_primary"], hover_color=COLORS["primary_container"], command=self._save_route).pack(side="left")

    def _add_form_field(self, parent, label_text, placeholder, is_dropdown=False, disabled=False):
        wrapper = ctk.CTkFrame(parent, fg_color="transparent")
        wrapper.pack(fill="x", pady=8)
        ctk.CTkLabel(wrapper, text=label_text, font=FONTS["label_md"], text_color=COLORS["on_surface"]).pack(anchor="w", pady=(0, 4))
        
        bg = COLORS["surface_variant"] if disabled else COLORS["surface_container_lowest"]
        tc = COLORS["on_surface_variant"] if disabled else COLORS["on_surface"]
        
        entry = ctk.CTkEntry(wrapper, font=FONTS["body_md"], fg_color=bg, text_color=tc, border_color=COLORS["outline_variant"], placeholder_text=placeholder, height=36)
        entry.pack(fill="x")
        if disabled:
            entry.insert(0, placeholder)
            entry.configure(state="disabled")
        elif is_dropdown:
            entry.insert(0, placeholder)
            
        return entry
        
    def _save_route(self):
        r_id = self.entry_id.get().strip()
        src = self.entry_src.get().strip()
        dst = self.entry_dst.get().strip()
        stops = self.entry_stops.get().strip()
        
        dist_str = self.entry_dist.get().strip()
        dur_str = self.entry_dur.get().strip()
        
        dist = int(dist_str) if dist_str.isdigit() else 100
        dur = int(dur_str) if dur_str.isdigit() else 120
        status = self.entry_status.get().strip()
        
        if r_id and src and dst:
            try:
                RouteModel.add_route(r_id, src, dst, stops, dist, dur, status)
                self._populate_grid()
                
                self.entry_id.delete(0, 'end')
                self.entry_src.delete(0, 'end')
                self.entry_dst.delete(0, 'end')
                self.entry_stops.delete(0, 'end')
                self.entry_dist.delete(0, 'end')
                self.entry_dur.delete(0, 'end')
                
                self.close_drawer()
            except Exception as e:
                print(f"Error saving route: {e}")
