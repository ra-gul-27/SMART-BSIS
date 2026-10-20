import customtkinter as ctk
from app.constants import COLORS, FONTS
from app.models.anpr_record_model import ANPRRecordModel

class ANPRRecordsView(ctk.CTkFrame):
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
        self.content_grid.grid_columnconfigure(0, weight=1)
        
        self._build_table_panel(self.content_grid)
        self._build_sidebar(self.content_grid)

    def _build_header(self):
        header = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 16))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=1)

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(left, text="ANPR Records", font=FONTS["headline_lg"], text_color=COLORS["on_surface"]).pack(anchor="w")
        ctk.CTkLabel(left, text="Monitor and verify automatic number plate recognition events.", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e", pady=(16, 0))

        date_sel = ctk.CTkEntry(right, placeholder_text="📅 mm/dd/yyyy", font=FONTS["body_md"], fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], width=140, height=40)
        date_sel.pack(side="left", padx=(0, 12))

        cam_sel = ctk.CTkOptionMenu(right, values=["All Cameras", "CAM-01 (Entry)", "CAM-02 (Exit)"], font=FONTS["body_md"], fg_color=COLORS["surface_container_lowest"], button_color=COLORS["surface_container"], button_hover_color=COLORS["outline_variant"], text_color=COLORS["on_surface"], height=40)
        cam_sel.pack(side="left", padx=(0, 12))

        ctk.CTkButton(
            right, text="📥 Export CSV", font=FONTS["label_md"], height=40,
            fg_color=COLORS["primary"], text_color=COLORS["on_primary"], hover_color=COLORS["primary_container"]
        ).pack(side="left")

    def _build_table_panel(self, parent):
        table_card = ctk.CTkFrame(parent, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        table_card.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        
        # Header Row
        thead = ctk.CTkFrame(table_card, fg_color=COLORS["surface_container_low"], corner_radius=12)
        thead.pack(fill="x", padx=1, pady=1)
        th_row = ctk.CTkFrame(thead, fg_color="transparent")
        th_row.pack(fill="x", padx=16, pady=12)

        self.cols = [
            ("TIMESTAMP", 1.2), ("CAMERA", 1), ("REGISTRATION", 1.5), 
            ("MATCH/ROUTE", 1.5), ("BAY", 0.8), ("STATUS", 1)
        ]
        
        for i, (c, w) in enumerate(self.cols):
            th_row.grid_columnconfigure(i, weight=int(w*10), uniform="col")
            anchor = "w" if i < len(self.cols) - 1 else "e"
            sticky = "w" if anchor == "w" else "e"
            ctk.CTkLabel(th_row, text=c, font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).grid(row=0, column=i, sticky=sticky, padx=4)

        border1 = ctk.CTkFrame(table_card, fg_color=COLORS["outline_variant"], height=1)
        border1.pack(fill="x", padx=1)

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

        ctk.CTkLabel(tfoot_content, text="Showing 1 to 24 of 1,204 entries", font=("Inter", 12), text_color=COLORS["on_surface_variant"]).pack(side="left")
        
        pag_wrapper = ctk.CTkFrame(tfoot_content, fg_color="transparent")
        pag_wrapper.pack(side="right")
        
        for p in ["Prev", "1", "2", "3", "4", "5", "Next"]:
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

        records = ANPRRecordModel.get_all_records()

        for i, row in enumerate(records):
            is_verified = (row["match_status"] == "Verified")
            s_bg = "#d1fae5" if is_verified else "#fee2e2"
            s_fg = "#059669" if is_verified else COLORS["error"]
            reg_col = COLORS["on_surface"] if is_verified else COLORS["error"]
            bg_color = "transparent" if i % 2 == 0 else COLORS["surface_container"]
            if not is_verified:
                bg_color = COLORS["surface_bright"]
                
            tr = ctk.CTkFrame(self.grid_container, fg_color=bg_color, corner_radius=0)
            tr.pack(fill="x", padx=1)
            
            tr_content = ctk.CTkFrame(tr, fg_color="transparent")
            tr_content.pack(fill="x", padx=16, pady=12)
            
            for j, (c, w) in enumerate(self.cols):
                tr_content.grid_columnconfigure(j, weight=int(w*10), uniform="col")

            # Col 1: Timestamp
            c1 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c1.grid(row=0, column=0, sticky="ew", padx=4)
            # Format timestamp for UI
            ui_time = row["timestamp"].split(" ")[1] if " " in row["timestamp"] else row["timestamp"]
            ctk.CTkLabel(c1, text=ui_time, font=FONTS["data_mono"], text_color=COLORS["on_surface"]).pack(anchor="w")

            # Col 2: Camera
            c2 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c2.grid(row=0, column=1, sticky="ew", padx=4)
            ctk.CTkLabel(c2, text=row["camera_loc"], font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")

            # Col 3: Registration
            c3 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c3.grid(row=0, column=2, sticky="ew", padx=4)
            ctk.CTkLabel(c3, text=row["plate_number"], font=("Inter", 14, "bold"), text_color=reg_col).pack(anchor="w")

            # Col 4: Match/Route
            c4 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c4.grid(row=0, column=3, sticky="ew", padx=4)
            route = f"Confidence: {row['confidence']}%"
            ctk.CTkLabel(c4, text=route, font=FONTS["body_md"], text_color=COLORS["on_surface"] if is_verified else COLORS["on_surface_variant"]).pack(anchor="w")

            # Col 5: Bay
            c5 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c5.grid(row=0, column=4, sticky="ew", padx=4)
            ctk.CTkLabel(c5, text="--", font=FONTS["data_mono"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")

            # Col 6: Status
            c6 = ctk.CTkFrame(tr_content, fg_color="transparent")
            c6.grid(row=0, column=5, sticky="ew", padx=4)
            s_badge = ctk.CTkFrame(c6, fg_color=s_bg, border_color=s_bg, border_width=1, corner_radius=12)
            s_badge.pack(anchor="e")
            icon = "✓" if is_verified else "⚠"
            ctk.CTkLabel(s_badge, text=f"{icon} {row['match_status']}", text_color=s_fg, font=("Inter", 10, "bold")).pack(padx=8, pady=2)

            if i < len(records) - 1:
                border = ctk.CTkFrame(self.grid_container, fg_color=COLORS["outline_variant"], height=1)
                border.pack(fill="x", padx=1)

    def _build_sidebar(self, parent):
        side_panel = ctk.CTkFrame(parent, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12, width=360)
        side_panel.grid(row=0, column=1, sticky="nsew")
        side_panel.grid_propagate(False)

        # Header
        head = ctk.CTkFrame(side_panel, fg_color=COLORS["surface_container_low"], corner_radius=12)
        head.pack(fill="x", padx=1, pady=1)
        h_inner = ctk.CTkFrame(head, fg_color="transparent")
        h_inner.pack(fill="x", padx=16, pady=16)
        ctk.CTkLabel(h_inner, text="Capture Details", font=FONTS["headline_md"], text_color=COLORS["on_surface"]).pack(side="left")
        
        badge = ctk.CTkFrame(h_inner, fg_color=COLORS["surface_variant"], corner_radius=4)
        badge.pack(side="right")
        ctk.CTkLabel(badge, text="ID: ANP-8842", text_color=COLORS["on_surface_variant"], font=FONTS["data_mono"]).pack(padx=8, pady=2)

        # Scrollable Content
        body = ctk.CTkScrollableFrame(side_panel, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=16)

        # Image Container
        img_box = ctk.CTkFrame(body, fg_color="#213145", border_color=COLORS["outline_variant"], border_width=1, corner_radius=8, height=180)
        img_box.pack(fill="x", pady=(0, 16))
        img_box.pack_propagate(False)
        
        ctk.CTkLabel(img_box, text="[ Captured Bus Plate Image ]", text_color=COLORS["outline"], font=FONTS["label_md"]).place(relx=0.5, rely=0.4, anchor="center")
        
        ocr_box = ctk.CTkFrame(img_box, fg_color="#3B82F6", border_color="white", border_width=1, corner_radius=4)
        ocr_box.place(relx=0.5, rely=0.8, anchor="center")
        ctk.CTkLabel(ocr_box, text="TN 01 AB 1234", font=("Inter", 16, "bold"), text_color="white").pack(padx=12, pady=4)

        # Analysis Grid
        grid = ctk.CTkFrame(body, fg_color="transparent")
        grid.pack(fill="x", pady=(0, 16))
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        a1 = ctk.CTkFrame(grid, fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=8)
        a1.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        a1_inner = ctk.CTkFrame(a1, fg_color="transparent")
        a1_inner.pack(fill="both", expand=True, padx=12, pady=12)
        ctk.CTkLabel(a1_inner, text="OCR CONFIDENCE", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
        
        conf_row = ctk.CTkFrame(a1_inner, fg_color="transparent")
        conf_row.pack(fill="x", pady=(4, 0))
        ctk.CTkLabel(conf_row, text="96%", font=("Inter", 18, "bold"), text_color="#10b981").pack(side="left")
        
        bar_bg = ctk.CTkFrame(conf_row, fg_color=COLORS["surface_variant"], height=8, corner_radius=4)
        bar_bg.pack(side="left", fill="x", expand=True, padx=(8, 0))
        bar_fill = ctk.CTkFrame(bar_bg, fg_color="#10b981", corner_radius=4)
        bar_fill.place(relx=0, rely=0, relwidth=0.96, relheight=1.0)

        a2 = ctk.CTkFrame(grid, fg_color=COLORS["surface"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=8)
        a2.grid(row=0, column=1, sticky="ew")
        a2_inner = ctk.CTkFrame(a2, fg_color="transparent")
        a2_inner.pack(fill="both", expand=True, padx=12, pady=12)
        ctk.CTkLabel(a2_inner, text="PROCESSING TIME", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w")
        ctk.CTkLabel(a2_inner, text="124ms", font=("Inter", 18, "bold"), text_color=COLORS["on_surface"]).pack(anchor="w", pady=(4, 0))

        div = ctk.CTkFrame(body, fg_color=COLORS["outline_variant"], height=1)
        div.pack(fill="x", pady=16)

        # Matched Record Info
        ctk.CTkLabel(body, text="MATCHED BUS RECORD", font=FONTS["label_md"], text_color=COLORS["on_surface_variant"]).pack(anchor="w", pady=(0, 12))
        
        info = [
            ("Fleet ID", "BUS-402", COLORS["on_surface"]),
            ("Route", "Express Link", COLORS["on_surface"]),
            ("Operator", "Metro Transit Auth.", COLORS["on_surface"]),
            ("Schedule Status", "On Time (+1m)", "#10b981")
        ]

        for k, v, col in info:
            row = ctk.CTkFrame(body, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=k, font=FONTS["body_md"], text_color=COLORS["on_surface_variant"]).pack(side="left")
            ctk.CTkLabel(row, text=v, font=FONTS["body_md"], text_color=col).pack(side="right")

        # Action Footer
        foot = ctk.CTkFrame(side_panel, fg_color=COLORS["surface_container_lowest"], border_color=COLORS["outline_variant"], border_width=1, corner_radius=12)
        foot.pack(fill="x", side="bottom")
        
        f_inner = ctk.CTkFrame(foot, fg_color="transparent")
        f_inner.pack(fill="x", padx=16, pady=16)
        
        ctk.CTkButton(f_inner, text="Flag Review", font=FONTS["body_md"], text_color=COLORS["on_surface_variant"], fg_color="transparent", border_color=COLORS["outline_variant"], border_width=1, hover_color=COLORS["surface_container"], height=40, width=140).pack(side="left", padx=(0, 12))
        ctk.CTkButton(f_inner, text="Confirm Match", font=FONTS["body_md"], text_color=COLORS["on_primary"], fg_color=COLORS["primary"], hover_color=COLORS["primary_container"], height=40, width=140).pack(side="left", expand=True)
