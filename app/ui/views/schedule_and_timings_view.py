import customtkinter as ctk
from app.constants import COLORS, FONTS
from app.models.schedule_model import ScheduleModel
from app.db.database import get_connection

class ScheduleAndTimingsView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.app_controller = app_controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) 

        self.scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_container.grid(row=0, column=0, sticky="nsew")
        self.scroll_container.grid_columnconfigure(0, weight=1)

        self.route_filter_var = ctk.StringVar(value="")
        self.bay_filter_var = ctk.StringVar(value="")

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
        ctk.CTkLabel(left, text="Manage real-time bus departures, arrivals and bay allocations", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")

        # Today date indicator
        date_sel = ctk.CTkFrame(right, fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=8)
        date_sel.pack(side="left", padx=(0, 16))
        
        ctk.CTkLabel(date_sel, text="📅 Today (Live Schedules)", font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(side="left", padx=12, pady=6)

        ctk.CTkButton(
            right, text="+ Add Schedule", font=FONTS["label_md"], 
            fg_color=COLORS["primary"], text_color=COLORS["on_primary"], hover_color=COLORS["primary_container"],
            command=self._show_add_schedule_dialog
        ).pack(side="left")

    def _build_tabs(self):
        tab_container = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        tab_container.grid(row=1, column=0, sticky="ew", padx=32)
        
        bottom_border = ctk.CTkFrame(tab_container, fg_color=COLORS["outline_variant"], height=1)
        bottom_border.place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

        tab1 = ctk.CTkFrame(tab_container, fg_color="transparent")
        tab1.pack(side="left", padx=(0, 16))
        ctk.CTkLabel(tab1, text="☰ TABLE VIEW", font=("Inter", 12, "bold"), text_color=COLORS["primary"]).pack(pady=(8, 12), padx=8)
        
        indicator = ctk.CTkFrame(tab1, fg_color=COLORS["primary"], height=2)
        indicator.place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

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
        
        # Route filter with dynamic keyup listener
        self.route_entry = ctk.CTkEntry(
            left_filters, placeholder_text="Filter Route / Dest...", textvariable=self.route_filter_var,
            font=FONTS["body_md"], fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], 
            text_color=COLORS["on_surface"], width=170, height=32
        )
        self.route_entry.pack(side="left", padx=(0, 8))
        self.route_entry.bind("<KeyRelease>", lambda e: self._populate_grid())

        # Bay filter with dynamic keyup listener
        self.bay_entry = ctk.CTkEntry(
            left_filters, placeholder_text="Filter Bay (e.g. B01)...", textvariable=self.bay_filter_var,
            font=FONTS["body_md"], fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], 
            text_color=COLORS["on_surface"], width=160, height=32
        )
        self.bay_entry.pack(side="left")
        self.bay_entry.bind("<KeyRelease>", lambda e: self._populate_grid())
        
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
            ("DEPARTURE", 1.1), ("EST. ARRIVAL", 1.1), ("FARE", 0.9), ("STATUS", 1.4), ("ACTIONS", 1.1)
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

        self.count_label = ctk.CTkLabel(tfoot_content, text="Loading schedules...", font=("Inter", 12), text_color=COLORS["on_surface_variant"])
        self.count_label.pack(side="left")

    def _populate_grid(self):
        for widget in self.grid_container.winfo_children():
            widget.destroy()

        r_filter = self.route_filter_var.get().strip()
        b_filter = self.bay_filter_var.get().strip()
        schedules = ScheduleModel.get_all_schedules(route_filter=r_filter, bay_filter=b_filter)

        if hasattr(self, "count_label"):
            self.count_label.configure(text=f"Showing {len(schedules)} active schedules in terminal")

        for i, row in enumerate(schedules):
            sched_id = row["id"]
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
            tr_content.pack(fill="x", padx=16, pady=10)
            
            for j, (c, w) in enumerate(self.cols):
                tr_content.grid_columnconfigure(j, weight=int(w*10), uniform="col")

            # Col 1: Bus No
            c1 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c1.grid(row=0, column=0, sticky="ew", padx=4)
            ctk.CTkLabel(c1, text=row["bus"], font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(anchor="w")

            # Col 2: Route & Dest
            c2 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c2.grid(row=0, column=1, sticky="ew", padx=4)
            ctk.CTkLabel(c2, text=row["route"], font=("Inter", 13, "bold"), text_color=COLORS["on_surface"]).pack(anchor="w")
            ctk.CTkLabel(c2, text=row["dest"], font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")

            # Col 3: Bay
            c3 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c3.grid(row=0, column=2, sticky="ew", padx=4)
            ctk.CTkLabel(c3, text=row["bay"], font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(anchor="w")

            # Col 4: Departure
            c4 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c4.grid(row=0, column=3, sticky="ew", padx=4)
            overstruck = bool(strike)
            ctk.CTkLabel(c4, text=row["dep"], font=("Inter", 13, "overstrike" if overstruck else "normal"), text_color=COLORS["on_surface_variant"] if overstruck else COLORS["on_surface"]).pack(anchor="w")

            # Col 5: Est Arrival
            c5 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c5.grid(row=0, column=4, sticky="ew", padx=4)
            ctk.CTkLabel(c5, text=row["arr"], font=("Inter", 13), text_color=COLORS["on_surface"]).pack(anchor="w")

            # Col 6: Fare
            c6 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c6.grid(row=0, column=5, sticky="ew", padx=4)
            ctk.CTkLabel(c6, text=row["fare"], font=("Inter", 13, "bold"), text_color="#059669").pack(anchor="w")

            # Col 7: Status
            c7 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c7.grid(row=0, column=6, sticky="ew", padx=4)
            s_badge = ctk.CTkFrame(c7, fg_color=s_bg, border_color=s_b, border_width=1, corner_radius=12)
            s_badge.pack(anchor="w")
            ctk.CTkLabel(s_badge, text=status, text_color=s_fg, font=("Inter", 10, "bold")).pack(padx=8, pady=2)

            # Col 8: Actions (Cycle Status in PostgreSQL)
            c8 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c8.grid(row=0, column=7, sticky="ew", padx=4)
            c8_wrapper = ctk.CTkFrame(c8, fg_color="transparent")
            c8_wrapper.pack(anchor="e")
            
            # Interactive toggle button to change status in DB
            status_cycle_btn = ctk.CTkButton(
                c8_wrapper, text="⚡ Update", width=68, height=26, font=("Inter", 11),
                fg_color=COLORS["surface_container_high"], text_color=COLORS["primary"],
                border_color=COLORS["outline_variant"], border_width=1, hover_color=COLORS["surface_container_highest"],
                command=lambda sid=sched_id, cur_st=status: self._cycle_status(sid, cur_st)
            )
            status_cycle_btn.pack(side="left", padx=2)

            if i < len(schedules) - 1:
                border = ctk.CTkFrame(self.grid_container, fg_color=COLORS["outline_variant"], height=1)
                border.pack(fill="x", padx=1)

    def _cycle_status(self, sched_id, current_status):
        """Cycles schedule status through SCHEDULED -> BOARDING -> DEPARTED -> DELAYED in DB."""
        order = ["SCHEDULED", "BOARDING", "DEPARTED", "DELAYED"]
        cur = current_status.upper().strip()
        next_status = order[(order.index(cur) + 1) % len(order)] if cur in order else "BOARDING"
        ScheduleModel.update_schedule_status(sched_id, next_status)
        self._populate_grid()
        self._build_side_panel(self.content_grid)

    def _build_side_panel(self, parent):
        if hasattr(self, "side_panel_frame") and self.side_panel_frame is not None:
            self.side_panel_frame.destroy()

        self.side_panel_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.side_panel_frame.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        
        # 1. Bay Status Card (Live PostgreSQL data)
        bay_card = ctk.CTkFrame(self.side_panel_frame, fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        bay_card.pack(fill="x", pady=(0, 20))
        
        b_inner = ctk.CTkFrame(bay_card, fg_color="transparent")
        b_inner.pack(fill="x", padx=16, pady=16)
        
        ctk.CTkLabel(b_inner, text="🅿 Live Bay Allocation", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(anchor="w")
        ctk.CTkLabel(b_inner, text="Real-time terminal bay occupancy", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(0, 12))

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT pb.bay_id, pb.status, pb.vehicle_reg, s.destination, s.departure_time 
                FROM parking_bays pb
                LEFT JOIN schedules s ON s.bus_no = pb.vehicle_reg
                ORDER BY pb.bay_id LIMIT 5
            """)
            bays = cur.fetchall()
            conn.close()

            for bay_id, b_status, v_reg, dest, dep in bays:
                is_occ = b_status == "Occupied"
                c_bg = "#f0fdf4" if is_occ else "transparent"
                c_fg = "#10b981" if is_occ else COLORS["outline_variant"]
                icon = "✔" if is_occ else "○"
                title = f"{v_reg} (Docked)" if is_occ else "Available Bay"
                sub = f"Dest: {dest} • Dep: {dep}" if (is_occ and dest) else ("Ready for assignment" if not is_occ else "Docked at bay")

                item = ctk.CTkFrame(b_inner, fg_color=c_bg, border_color=COLORS["outline_variant"], border_width=1, corner_radius=8)
                item.pack(fill="x", pady=4)
                
                i_content = ctk.CTkFrame(item, fg_color="transparent")
                i_content.pack(fill="x", padx=8, pady=8)
                
                # Bay ID box
                box = ctk.CTkFrame(i_content, fg_color=COLORS["surface_container"], border_color=COLORS["outline_variant"], border_width=1, width=32, height=32, corner_radius=4)
                box.pack(side="left", padx=(0, 8))
                box.pack_propagate(False)
                ctk.CTkLabel(box, text=bay_id, font=("Inter", 11, "bold"), text_color=COLORS["on_surface"]).place(relx=0.5, rely=0.5, anchor="center")
                
                text_col = ctk.CTkFrame(i_content, fg_color="transparent")
                text_col.pack(side="left")
                ctk.CTkLabel(text_col, text=title, font=("Inter", 11, "bold"), text_color=COLORS["on_surface"] if is_occ else COLORS["on_surface_variant"]).pack(anchor="w")
                ctk.CTkLabel(text_col, text=sub, font=("Inter", 10), text_color=COLORS["on_surface_variant"]).pack(anchor="w")

                ctk.CTkLabel(i_content, text=icon, font=("Arial", 14), text_color=c_fg).pack(side="right", padx=6)
        except Exception as e:
            ctk.CTkLabel(b_inner, text=f"Notice: {e}", font=FONTS["label_md"]).pack()

        # 2. System Alerts Card (Live PostgreSQL events)
        alert_card = ctk.CTkFrame(self.side_panel_frame, fg_color=COLORS["surface"], border_color="#fecaca", border_width=1, corner_radius=12)
        alert_card.pack(fill="x")
        
        a_inner = ctk.CTkFrame(alert_card, fg_color="transparent")
        a_inner.pack(fill="x", padx=16, pady=16)
        
        ctk.CTkLabel(a_inner, text="⚠ Active Schedule Alerts", font=FONTS["headline_md"], text_color=COLORS["error"]).pack(anchor="w")
        
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, title, description FROM events WHERE event_type IN ('error', 'warning', 'primary') ORDER BY timestamp DESC LIMIT 1")
            alert_row = cur.fetchone()
            conn.close()

            if alert_row:
                ev_id, ev_title, ev_desc = alert_row
                clean_title = str(ev_title).encode('ascii', 'replace').decode('ascii')
                clean_desc = str(ev_desc).encode('ascii', 'replace').decode('ascii') if ev_desc else "Active monitoring."
                ctk.CTkLabel(a_inner, text=clean_title, font=("Inter", 12, "bold"), text_color=COLORS["on_surface"]).pack(anchor="w", pady=(8, 2))
                ctk.CTkLabel(a_inner, text=clean_desc, font=FONTS["label_md"], text_color=COLORS["on_surface_variant"], wraplength=220, justify="left").pack(anchor="w", pady=(0, 12))
            else:
                ctk.CTkLabel(a_inner, text="All bus departures operating normally on schedule.", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=8)

            ack_btn = ctk.CTkButton(
                a_inner, text="✔ Acknowledge & Sync Feed", font=("Inter", 12, "bold"), 
                text_color=COLORS["error"], fg_color="transparent", hover_color="#fee2e2", anchor="w",
                command=self._acknowledge_alert
            )
            ack_btn.pack(anchor="w", fill="x")
        except Exception as e:
            ctk.CTkLabel(a_inner, text=f"Alerts load notice: {e}", font=FONTS["label_md"]).pack()

    def _acknowledge_alert(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO events (title, description, event_type) VALUES ('Alert Acknowledged', 'Operator verified terminal schedule status.', 'info')")
            conn.commit()
            conn.close()
        except Exception:
            pass
        self._build_side_panel(self.content_grid)

    def _show_add_schedule_dialog(self):
        """Interactive modal dialog to add a new schedule directly to PostgreSQL."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Schedule & Timing")
        dialog.geometry("440x520")
        dialog.configure(fg_color=COLORS["surface"])
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="New Departure Schedule", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(padx=24, pady=(20, 12), anchor="w")

        entries = {}
        fields = [
            ("Bus Registration No", "bus", "TN 01 AN 2345"),
            ("Route Name", "route", "R-01 (Chennai - Bangalore)"),
            ("Destination", "dest", "Bangalore Shantinagar"),
            ("Parking Bay", "bay", "B02"),
            ("Departure Time", "dep", "02:30 PM"),
            ("Est. Arrival Time", "arr", "08:30 PM"),
            ("Ticket Fare", "fare", "Rs 650.00"),
        ]

        for label_text, key, placeholder in fields:
            f = ctk.CTkFrame(dialog, fg_color="transparent")
            f.pack(fill="x", padx=24, pady=3)
            ctk.CTkLabel(f, text=label_text, font=FONTS["label_md"], text_color=COLORS["on_surface_variant"], width=140, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(f, placeholder_text=placeholder, font=FONTS["body_md"], height=28, fg_color=COLORS["surface_container_low"])
            entry.pack(side="right", fill="x", expand=True)
            entry.insert(0, placeholder)
            entries[key] = entry

        def save():
            try:
                ScheduleModel.add_schedule(
                    entries["bus"].get().strip(),
                    entries["route"].get().strip(),
                    entries["dest"].get().strip(),
                    entries["bay"].get().strip(),
                    entries["dep"].get().strip(),
                    entries["arr"].get().strip(),
                    entries["fare"].get().strip(),
                    "SCHEDULED"
                )
                dialog.destroy()
                self._populate_grid()
                self._build_side_panel(self.content_grid)
            except Exception as e:
                print(f"Error saving schedule: {e}")

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=20)
        ctk.CTkButton(btn_row, text="Cancel", font=FONTS["label_md"], fg_color="transparent", text_color=COLORS["on_surface"], command=dialog.destroy).pack(side="left")
        ctk.CTkButton(btn_row, text="Save Schedule", font=FONTS["label_md"], fg_color=COLORS["primary"], text_color=COLORS["on_primary"], command=save).pack(side="right")
