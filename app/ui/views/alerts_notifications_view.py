import customtkinter as ctk
from app.constants import COLORS, FONTS
from app.db.database import get_connection

class AlertsNotificationsView(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        self.app_controller = app_controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) 

        self.current_filter = "ALL"

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
        
        ctk.CTkLabel(header, text="Alerts & System Notifications", font=FONTS["headline_lg"], text_color=COLORS["on_surface"]).pack(anchor="w")
        ctk.CTkLabel(header, text="Monitor AI terminal events, camera conflicts and operational alerts in real time", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")

    def _build_kpi_cards(self):
        kpi_container = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        kpi_container.grid(row=1, column=0, sticky="ew", padx=32)
        
        for i in range(4):
            kpi_container.grid_columnconfigure(i, weight=1, uniform="kpi")

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM events")
            total_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM events WHERE event_type = 'error'")
            crit_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM events WHERE event_type = 'warning'")
            warn_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM events WHERE event_type IN ('primary', 'info')")
            ops_count = cur.fetchone()[0]
            conn.close()
        except Exception:
            total_count, crit_count, warn_count, ops_count = 12, 0, 1, 11

        kpis = [
            {"title": "TOTAL EVENTS", "val": str(total_count), "sub": "Logged in terminal", "color": COLORS["primary"], "border": COLORS["outline_variant"], "bg": COLORS["surface"]},
            {"title": "CRITICAL ALERTS", "val": str(crit_count), "sub": "Requires attention", "color": COLORS["error"] if crit_count > 0 else "#10b981", "border": "#fca5a5" if crit_count > 0 else COLORS["outline_variant"], "bg": COLORS["surface"]},
            {"title": "WARNINGS", "val": str(warn_count), "sub": "Sensor latency / drift", "color": "#f59e0b", "border": "#fcd34d", "bg": COLORS["surface"]},
            {"title": "AI & OPERATIONAL", "val": str(ops_count), "sub": "ANPR & bay dockings", "color": "#059669", "border": "#a7f3d0", "bg": COLORS["surface"]}
        ]

        for i, kpi in enumerate(kpis):
            card = ctk.CTkFrame(kpi_container, fg_color=kpi["bg"], border_color=kpi["border"], border_width=1, corner_radius=12, height=110)
            card.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 8, 0 if i == 3 else 8))
            card.pack_propagate(False)
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=16, pady=14)

            ctk.CTkLabel(inner, text=kpi["title"], font=("Inter", 11, "bold"), text_color=kpi["color"]).pack(anchor="w")
            ctk.CTkLabel(inner, text=kpi["val"], font=("Inter", 28, "bold"), text_color=kpi["color"]).pack(anchor="w", pady=(2, 4))
            ctk.CTkLabel(inner, text=kpi["sub"], font=("Inter", 11), text_color=COLORS["on_surface_variant"]).pack(anchor="w")

    def _build_table_panel(self, parent):
        table_card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        table_card.grid(row=0, column=0, sticky="nsew")
        
        # Header Row with Filter Buttons
        thead = ctk.CTkFrame(table_card, fg_color=COLORS["surface_container_lowest"], corner_radius=12)
        thead.pack(fill="x", padx=1, pady=1)
        th_inner = ctk.CTkFrame(thead, fg_color="transparent")
        th_inner.pack(fill="x", padx=16, pady=12)
        
        ctk.CTkLabel(th_inner, text="Real-Time Terminal Events & Alerts Stream", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(side="left")
        
        filter_box = ctk.CTkFrame(th_inner, fg_color="transparent")
        filter_box.pack(side="right")
        
        for f in ["ALL", "CRITICAL", "WARNINGS", "OPERATIONAL"]:
            is_active = (self.current_filter == f)
            bg = COLORS["primary"] if is_active else "transparent"
            tc = "#ffffff" if is_active else COLORS["on_surface_variant"]
            b_width = 0 if is_active else 1
            btn = ctk.CTkButton(
                filter_box, text=f, width=75, height=28, font=("Inter", 10, "bold"),
                fg_color=bg, text_color=tc, border_color=COLORS["outline_variant"], border_width=b_width,
                hover_color=COLORS["surface_container"],
                command=lambda opt=f: self._set_filter(opt)
            )
            btn.pack(side="left", padx=2)

        border1 = ctk.CTkFrame(table_card, fg_color=COLORS["outline_variant"], height=1)
        border1.pack(fill="x", padx=1)

        # Col headers
        self.cols = [
            ("ICON", 0.4), ("TYPE & TIMESTAMP", 1.5), ("ALERT TITLE & DESCRIPTION", 4.0), ("ACTIONS", 1.8)
        ]
        
        th_row = ctk.CTkFrame(table_card, fg_color=COLORS["surface_container_low"])
        th_row.pack(fill="x", padx=1)
        th_r_inner = ctk.CTkFrame(th_row, fg_color="transparent")
        th_r_inner.pack(fill="x", padx=16, pady=8)

        for i, (c, w) in enumerate(self.cols):
            th_r_inner.grid_columnconfigure(i, weight=int(w*10), uniform="col")
            anchor = "w" if i < len(self.cols) - 1 else "e"
            sticky = "w" if anchor == "w" else "e"
            ctk.CTkLabel(th_r_inner, text=c if c != "ICON" else "", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).grid(row=0, column=i, sticky=sticky, padx=4)

        border2 = ctk.CTkFrame(table_card, fg_color=COLORS["outline_variant"], height=1)
        border2.pack(fill="x", padx=1)

        # Table Body
        self.body_container = ctk.CTkFrame(table_card, fg_color="transparent")
        self.body_container.pack(fill="x")
        self._populate_alerts()

    def _set_filter(self, filter_name):
        self.current_filter = filter_name
        self._populate_alerts()

    def _populate_alerts(self):
        for child in self.body_container.winfo_children():
            child.destroy()

        try:
            conn = get_connection()
            cur = conn.cursor()
            
            query = "SELECT id, timestamp, title, description, event_type FROM events WHERE 1=1"
            if self.current_filter == "CRITICAL":
                query += " AND event_type = 'error'"
            elif self.current_filter == "WARNINGS":
                query += " AND event_type = 'warning'"
            elif self.current_filter == "OPERATIONAL":
                query += " AND event_type IN ('primary', 'info')"
                
            query += " ORDER BY timestamp DESC LIMIT 20"
            cur.execute(query)
            rows = cur.fetchall()
            conn.close()
        except Exception as e:
            rows = []

        if not rows:
            empty_box = ctk.CTkFrame(self.body_container, fg_color="transparent")
            empty_box.pack(fill="x", pady=24)
            ctk.CTkLabel(empty_box, text="No events found for selected filter.", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack()
            return

        for i, (ev_id, ts, title, desc, ev_type) in enumerate(rows):
            raw_time = str(ts)
            time_str = raw_time.split(" ")[1].split(".")[0] if " " in raw_time else raw_time
            clean_title = str(title).encode('ascii', 'replace').decode('ascii')
            clean_desc = str(desc).encode('ascii', 'replace').decode('ascii') if desc else ""

            is_error = ev_type == "error"
            is_warning = ev_type == "warning"

            if is_error:
                icon = "❌"
                icon_col = COLORS["error"]
                badge_text = "CRITICAL"
                badge_bg = "#fee2e2"
                badge_fg = COLORS["error"]
                bg_col = "#fefcfc"
            elif is_warning:
                icon = "⚠"
                icon_col = "#f59e0b"
                badge_text = "WARNING"
                badge_bg = "#fef3c7"
                badge_fg = "#b45309"
                bg_col = "#fffdf7"
            else:
                icon = "✔"
                icon_col = "#10b981"
                badge_text = "AI EVENT"
                badge_bg = "#d1fae5"
                badge_fg = "#059669"
                bg_col = "transparent" if i % 2 == 0 else COLORS["surface_container_low"]

            tr = ctk.CTkFrame(self.body_container, fg_color=bg_col, corner_radius=0)
            tr.pack(fill="x", padx=1)
            
            tr_content = ctk.CTkFrame(tr, fg_color="transparent")
            tr_content.pack(fill="x", padx=16, pady=12)
            
            for j, (c, w) in enumerate(self.cols):
                tr_content.grid_columnconfigure(j, weight=int(w*10), uniform="col")

            # Col 1: Icon
            c1 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c1.grid(row=0, column=0, sticky="ew", padx=4)
            ctk.CTkLabel(c1, text=icon, font=("Arial", 16), text_color=icon_col).pack(anchor="w")

            # Col 2: Type & Timestamp
            c2 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c2.grid(row=0, column=1, sticky="ew", padx=4)
            badge = ctk.CTkFrame(c2, fg_color=badge_bg, corner_radius=10)
            badge.pack(anchor="w", pady=(0, 2))
            ctk.CTkLabel(badge, text=badge_text, font=("Inter", 9, "bold"), text_color=badge_fg).pack(padx=6, pady=1)
            ctk.CTkLabel(c2, text=time_str, font=FONTS["data_mono"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")

            # Col 3: Details
            c3 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c3.grid(row=0, column=2, sticky="ew", padx=4)
            ctk.CTkLabel(c3, text=clean_title, font=("Inter", 13, "bold"), text_color=COLORS["on_surface"]).pack(anchor="w")
            if clean_desc:
                ctk.CTkLabel(c3, text=clean_desc, font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(2, 0))

            # Col 4: Actions
            c4 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c4.grid(row=0, column=3, sticky="ew", padx=4)
            act_wrapper = ctk.CTkFrame(c4, fg_color="transparent")
            act_wrapper.pack(anchor="e")
            
            # Action 1: View Camera
            ctk.CTkButton(
                act_wrapper, text="📹 View AI Stream", width=105, height=26, font=("Inter", 10, "bold"),
                fg_color=COLORS["surface_container_high"], text_color=COLORS["primary"],
                border_color=COLORS["outline_variant"], border_width=1, hover_color=COLORS["surface_container_highest"],
                command=lambda: self.app_controller.show_view("LiveMonitoring2") if self.app_controller else None
            ).pack(side="left", padx=2)

            # Action 2: Resolve / Dismiss
            ctk.CTkButton(
                act_wrapper, text="✔ Resolve", width=70, height=26, font=("Inter", 10, "bold"),
                fg_color="#059669" if is_error else COLORS["primary"], text_color="#ffffff",
                command=lambda eid=ev_id, etitle=clean_title: self._resolve_event(eid, etitle)
            ).pack(side="left", padx=2)

            if i < len(rows) - 1:
                border = ctk.CTkFrame(self.body_container, fg_color=COLORS["outline_variant"], height=1)
                border.pack(fill="x", padx=1)

    def _resolve_event(self, event_id, event_title):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM events WHERE id = %s", (event_id,))
            cur.execute("INSERT INTO events (title, description, event_type) VALUES (%s, 'Resolved by terminal supervisor.', 'info')", (f"Resolved: {event_title}",))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error resolving event: {e}")
            
        self._build_kpi_cards()
        self._populate_alerts()
